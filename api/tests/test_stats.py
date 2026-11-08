from netflix_history_api.parsing import read_history
from netflix_history_api.sample import sample_csv
from netflix_history_api.stats import analyse


def history(*rows: tuple[str, str]) -> dict:
    # Netflix lists newest first; the tests write rows oldest first for readability.
    body = "".join(f'"{t}","{d}"\n' for t, d in reversed(rows))
    return analyse(read_history(("Title,Date\n" + body).encode()))


ROWS = [
    ("Signal Lost: Season 1: A (Episode 1)", "01/03/2023"),
    ("Signal Lost: Season 1: B (Episode 2)", "01/03/2023"),
    ("Signal Lost: Season 1: C (Episode 3)", "01/03/2023"),  # a binge: 3 in a day
    ("Quiet Film", "02/03/2023"),
    ("Signal Lost: Season 2: D (Episode 1)", "03/03/2023"),
    ("Quiet Film", "10/03/2023"),  # rewatch, after a 6-day break
    ("Northbound: Season 1: E (Episode 1)", "15/01/2024"),
]


def test_totals():
    t = history(*ROWS)["totals"]
    assert t["shows"] == 5 and t["movies"] == 2
    assert t["activeDays"] == 5
    assert t["longestStreak"] == 3
    assert t["longestBreak"] == {"days": 310, "from": "2023-03-11", "to": "2024-01-14"}
    assert t["bingeSessions"] == 1
    assert t["bingeShare"] == 60  # 3 of 5 episodes
    assert t["rewatches"] == 1


def test_yearly_counts_new_titles_once():
    y = {r["year"]: r for r in history(*ROWS)["yearly"]}
    assert (y[2023]["newShows"], y[2023]["newMovies"]) == (1, 1)
    assert (y[2024]["newShows"], y[2024]["newMovies"]) == (1, 0)
    assert y[2023]["activeDays"] == 4


def test_deep_dive():
    top = history(*ROWS)["shows"][0]
    assert top["name"] == "Signal Lost"
    picked = {k: top[k] for k in ("plays", "episodes", "seasons", "days", "binges")}
    assert picked == {"plays": 4, "episodes": 4, "seasons": 2, "days": 2, "binges": 1}
    assert top["byYear"] == [4, 0]


def test_highlights_and_insights():
    out = history(*ROWS)
    keys = {h["key"] for h in out["highlights"]}
    assert {"topShow", "biggestBinge", "longestBreak", "mostRewatched", "firstWatched"} <= keys
    rewatch = next(h for h in out["highlights"] if h["key"] == "mostRewatched")
    assert (rewatch["value"], rewatch["sub"]) == ("Quiet Film", "2 times")
    assert all(i["text"].endswith(".") for i in out["insights"])


def test_single_title_does_not_crash():
    out = history(("Only Film", "01/01/2024"))
    assert out["totals"]["longestBreak"]["days"] == 0
    assert out["shows"] == []


def test_sample_shape():
    out = analyse(read_history(sample_csv()))
    assert out["meta"]["dateOrder"] == "dmy"
    assert sum(r[4] + r[5] for r in out["daily"]) == out["meta"]["records"]
    assert sum(t[3] for t in out["titles"]) == out["meta"]["records"]
    assert sum(y["shows"] + y["movies"] for y in out["yearly"]) == out["meta"]["records"]
    assert len(out["highlights"]) == 16
    assert len(out["shows"]) == 12
