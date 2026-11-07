import pytest
from fastapi.testclient import TestClient

from netflix_history_api.analysis import HistoryError, analyse, read_history
from netflix_history_api.app import app
from netflix_history_api.sample import sample_csv


def csv(*rows: tuple[str, str]) -> bytes:
    return ("Title,Date\n" + "".join(f'"{t}","{d}"\n' for t, d in rows)).encode()


def test_uk_dates_are_read_day_first():
    parsed = read_history(csv(("A Film", "25/12/2021"), ("B Film", "10/12/2021")))
    assert parsed.date_order == "dmy"
    assert parsed.frame["date"].dt.strftime("%Y-%m-%d").tolist() == ["2021-12-25", "2021-12-10"]


def test_us_short_dates_are_read_month_first():
    parsed = read_history(csv(("A Film", "12/25/21"), ("B Film", "12/10/21")))
    assert parsed.date_order == "mdy"
    assert parsed.frame["date"].dt.month.tolist() == [12, 12]


def test_ambiguous_dates_use_newest_first_ordering():
    # Every day <= 12. Read day-first these run 3 Feb, 2 Feb, 1 Feb (newest first).
    rows = [("X", "03/02/2022"), ("Y", "02/02/2022"), ("Z", "01/02/2022"), ("W", "12/01/2022")]
    parsed = read_history(csv(*rows))
    assert parsed.date_order == "dmy"


def test_date_order_override():
    parsed = read_history(csv(("X", "03/02/2022")), date_order="mdy")
    assert parsed.frame["date"].iloc[0].month == 3


def test_classification():
    parsed = read_history(csv(
        ("Signal Lost: Season 2: Undertow", "01/01/2023"),
        ("Northbound: Limited Series: Part 1", "01/01/2023"),
        ("Mission: Impossible", "01/01/2023"),
        ("Plain Film", "01/01/2023"),
    ))
    kinds = dict(zip(parsed.frame["title"], parsed.frame["kind"], strict=True))
    assert kinds["Signal Lost: Season 2: Undertow"] == "show"
    assert kinds["Northbound: Limited Series: Part 1"] == "show"
    assert kinds["Mission: Impossible"] == "movie"
    names = dict(zip(parsed.frame["title"], parsed.frame["name"], strict=True))
    assert names["Mission: Impossible"] == "Mission: Impossible"
    assert names["Signal Lost: Season 2: Undertow"] == "Signal Lost"


def test_viewing_activity_format_drops_trailers():
    raw = (b"Profile Name,Start Time,Duration,Title,Supplemental Video Type\n"
           b"Me,2023-05-01 21:00:00,00:40:00,Saltmarsh: Season 1: Arrival,\n"
           b"Me,2023-05-01 20:58:00,00:01:00,Saltmarsh: Season 1 (Trailer),TRAILER\n")
    parsed = read_history(raw)
    assert len(parsed.frame) == 1


def test_rejects_non_history():
    with pytest.raises(HistoryError):
        read_history(b"foo,bar\n1,2\n")


def test_analyse_sample_shape():
    out = analyse(read_history(sample_csv()))
    assert out["meta"]["dateOrder"] == "dmy"
    assert out["meta"]["last"] == "2025-10-31"
    assert sum(r[4] + r[5] for r in out["daily"]) == out["meta"]["records"]
    assert sum(t[3] for t in out["titles"]) == out["meta"]["records"]
    assert {h["key"] for h in out["highlights"]} >= {"topShow", "topMovie", "biggestBinge"}


def test_api_upload_roundtrip():
    client = TestClient(app)
    r = client.post("/api/analyze", files={"file": ("h.csv", csv(("A Film", "25/12/2021")))})
    assert r.status_code == 200
    assert r.json()["meta"]["first"] == "2021-12-25"
    bad = client.post("/api/analyze", files={"file": ("h.csv", b"nope")})
    assert bad.status_code == 422
