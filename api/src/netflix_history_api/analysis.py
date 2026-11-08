"""Turn a Netflix viewing-history CSV into the JSON the dashboard draws.

Python does all the parsing, cleaning, classification and aggregation here.
The frontend only sums the pre-aggregated slices when a filter changes.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from typing import Literal

import pandas as pd

DateOrder = Literal["auto", "dmy", "mdy"]

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# A second title segment like "Season 2", "Limited Series", "Part 1" marks a TV episode.
_EPISODIC = re.compile(
    r"^(season|series|part|volume|vol\.|chapter|book|collection|limited series|"
    r"miniseries|episode|staffel|temporada|saison)\b",
    re.IGNORECASE,
)


class HistoryError(ValueError):
    """The uploaded file can't be read as a Netflix viewing history."""


@dataclass(frozen=True)
class Parsed:
    frame: pd.DataFrame
    date_order: Literal["dmy", "mdy", "iso"]


# ---------------------------------------------------------------- parsing


def read_history(raw: bytes, date_order: DateOrder = "auto") -> Parsed:
    """Read either export format Netflix offers.

    * ``NetflixViewingHistory.csv`` (Account > Viewing activity > Download all): Title, Date
    * ``ViewingActivity.csv`` (full data request): Profile Name, Start Time, ..., Title, ...
    """
    try:
        df = pd.read_csv(io.BytesIO(raw), dtype=str, keep_default_na=False)
    except (pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise HistoryError("That file isn't a readable CSV.") from exc

    df.columns = [c.strip() for c in df.columns]
    if {"Title", "Date"} <= set(df.columns):
        df = df[["Title", "Date"]]
        dates, order = _parse_dates(df["Date"], date_order)
    elif {"Title", "Start Time"} <= set(df.columns):
        if "Supplemental Video Type" in df.columns:  # drop trailers, teasers, recaps
            df = df[df["Supplemental Video Type"].str.strip() == ""]
        df = df[["Title", "Start Time"]].rename(columns={"Start Time": "Date"})
        dates, order = pd.to_datetime(df["Date"], errors="coerce").dt.normalize(), "iso"
    else:
        raise HistoryError("Expected a Netflix history CSV with Title and Date columns.")

    df = df.assign(Title=df["Title"].str.strip(), Date=dates)
    df = df[(df["Title"] != "") & df["Date"].notna()]
    if df.empty:
        raise HistoryError("No viewing records found in that file.")
    return Parsed(_enrich(df.reset_index(drop=True)), order)


def _parse_dates(col: pd.Series, date_order: DateOrder) -> tuple[pd.Series, str]:
    """Parse slash dates, working out day/month order when it's ambiguous.

    Netflix writes dates in the account's locale (UK ``31/12/2023``, US ``12/31/23``).
    The old dashboard always read them month-first, so every UK date with a day
    of 12 or less landed in the wrong month.
    """
    s = col.str.strip()
    if s.str.match(r"^\d{4}-\d{2}-\d{2}").all():
        return pd.to_datetime(s, format="ISO8601", errors="coerce").dt.normalize(), "iso"

    parts = s.str.split("/", expand=True)
    if parts.shape[1] != 3:
        raise HistoryError("Dates must look like 31/12/2023 or 12/31/23.")
    year_fmt = "%Y" if parts[2].str.len().max() > 2 else "%y"
    dmy = pd.to_datetime(s, format=f"%d/%m/{year_fmt}", errors="coerce")
    mdy = pd.to_datetime(s, format=f"%m/%d/{year_fmt}", errors="coerce")

    if date_order == "auto":
        bad_dmy, bad_mdy = dmy.isna().sum(), mdy.isna().sum()
        if bad_dmy != bad_mdy:
            date_order = "dmy" if bad_dmy < bad_mdy else "mdy"
        else:
            # Every day is 12 or less: Netflix lists newest first, so the right
            # reading is the one that's closest to sorted descending.
            date_order = "dmy" if _disorder(dmy) <= _disorder(mdy) else "mdy"

    return (dmy if date_order == "dmy" else mdy), date_order


def _disorder(dates: pd.Series) -> int:
    d = dates.dropna()
    return int((d.diff().dt.days > 0).sum())


def _enrich(df: pd.DataFrame) -> pd.DataFrame:
    parts = (df["Title"].str.split(": ", n=2, expand=True)
             .reindex(columns=[0, 1, 2], fill_value="").fillna(""))
    prefix, second, rest = parts[0], parts[1], parts[2]

    # An episode either says so ("Season 1", "Limited Series") or its prefix
    # turns up with several different full titles (an untagged series).
    titles_per_prefix = df.groupby(prefix)["Title"].transform("nunique")
    is_show = second.str.match(_EPISODIC) | ((rest != "") & (titles_per_prefix >= 2))

    dates = df["Date"]
    return pd.DataFrame({
        "date": dates,
        "title": df["Title"],
        "kind": is_show.map({True: "show", False: "movie"}),
        # A movie keeps its whole title, so "Mission: Impossible" stays one name.
        "name": prefix.where(is_show, df["Title"]),
        "season": second.where(is_show, ""),
        "episode": rest.where(is_show, ""),
        "year": dates.dt.year,
        "month": dates.dt.month,
        "day": dates.dt.day,
        "weekday": dates.dt.day_of_week,
    }).sort_values("date", ascending=False, kind="stable").reset_index(drop=True)


# ---------------------------------------------------------------- analysis


def analyse(parsed: Parsed) -> dict:
    df = parsed.frame
    shows, movies = df[df["kind"] == "show"], df[df["kind"] == "movie"]
    per_day = df.groupby("date").size()

    return {
        "meta": {
            "records": len(df),
            "first": df["date"].min().date().isoformat(),
            "last": df["date"].max().date().isoformat(),
            "years": sorted(int(y) for y in df["year"].unique()),
            "dateOrder": parsed.date_order,
        },
        "totals": {
            "shows": len(shows),
            "movies": len(movies),
            "distinctShows": int(shows["name"].nunique()),
            "distinctMovies": int(movies["name"].nunique()),
            "activeDays": len(per_day),
            "longestStreak": _longest_streak(per_day.index),
        },
        "highlights": _highlights(df, shows, movies, per_day),
        # [year, month, day, weekday, shows, movies] per active date
        "daily": _daily(df),
        # [name, kind, year, count] — summed client-side for any year range
        "titles": _titles(df),
        "history": df.assign(date=df["date"].dt.strftime("%Y-%m-%d"))[
            ["date", "title", "kind", "name", "season", "episode"]
        ].to_dict("records"),
    }


def _top(series: pd.Series) -> tuple[object, int] | None:
    if series.empty:
        return None
    counts = series.value_counts()
    return counts.index[0], int(counts.iloc[0])


def _highlights(df, shows, movies, per_day) -> list[dict]:
    out: list[dict] = []

    def add(key, label, top, fmt=str):
        if top:
            out.append({"key": key, "label": label, "value": fmt(top[0]), "count": top[1]})

    add("topShow", "Top show", _top(shows["name"]))
    add("topMovie", "Top movie", _top(movies["name"]))
    add("busiestYear", "Busiest year", _top(df["year"]))
    add("busiestMonth", "Busiest month", _top(df["month"]), lambda m: MONTHS[m - 1])
    add("favouriteWeekday", "Favourite day", _top(df["weekday"]), lambda d: WEEKDAYS[d])
    add("busiestDayOfMonth", "Busiest date of the month", _top(df["day"]), _ordinal)

    if not per_day.empty:
        day = per_day.idxmax()
        out.append({"key": "biggestDay", "label": "Biggest day",
                    "value": _day(day), "count": int(per_day.max())})
    if not shows.empty:
        binge = shows.groupby(["date", "name"]).size()
        (date, name), n = binge.idxmax(), int(binge.max())
        out.append({"key": "biggestBinge", "label": "Biggest binge",
                    "value": name, "count": n, "detail": _day(date)})
    return out


def _longest_streak(dates: pd.DatetimeIndex) -> int:
    if len(dates) == 0:
        return 0
    d = pd.Series(dates.sort_values())
    run_id = (d.diff().dt.days != 1).cumsum()
    return int(run_id.value_counts().max())


def _daily(df: pd.DataFrame) -> list[list[int]]:
    g = (df.pivot_table(index="date", columns="kind", values="title", aggfunc="size", fill_value=0)
           .reindex(columns=["show", "movie"], fill_value=0)
           .sort_index())
    idx = g.index
    return [[int(y), int(m), int(d), int(w), int(s), int(v)]
            for y, m, d, w, s, v in zip(idx.year, idx.month, idx.day, idx.day_of_week,
                                        g["show"], g["movie"], strict=True)]


def _titles(df: pd.DataFrame) -> list[list]:
    g = df.groupby(["name", "kind", "year"]).size().reset_index(name="n")
    return [[r.name, r.kind, int(r.year), int(r.n)] for r in g.itertuples(index=False)]


def _day(ts: pd.Timestamp) -> str:
    # "%-d" (no leading zero) is not supported by strftime on Windows.
    return f"{ts.day} {ts:%b %Y}"


def _ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
