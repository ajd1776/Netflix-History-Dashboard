"""Read a Netflix viewing-history CSV into a clean, enriched DataFrame.

One row per play, newest first, with the show/movie split worked out.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from typing import Literal

import pandas as pd

DateOrder = Literal["auto", "dmy", "mdy"]

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
