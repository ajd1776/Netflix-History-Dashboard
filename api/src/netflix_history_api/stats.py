"""Everything the dashboard shows, worked out from the parsed history.

Python does all the analysis here. The page only re-sums the `daily` and
`titles` slices when a filter changes; everything else is ready to draw.
"""

from __future__ import annotations

import pandas as pd

from .parsing import Parsed

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SEASON_OF_MONTH = {12: "Winter", 1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring",
                   5: "Spring", 6: "Summer", 7: "Summer", 8: "Summer", 9: "Autumn",
                   10: "Autumn", 11: "Autumn"}
BINGE = 3  # episodes of one show in a day
DEEP_DIVE = 12  # shows in the deep-dive table


class _History:
    """The parsed frame plus the groupings several statistics share."""

    def __init__(self, parsed: Parsed):
        df = parsed.frame
        self.df = df
        self.date_order = parsed.date_order
        self.shows = df[df["kind"] == "show"]
        self.movies = df[df["kind"] == "movie"]
        self.years = sorted(int(y) for y in df["year"].unique())
        self.first, self.last = df["date"].min(), df["date"].max()
        self.span_days = (self.last - self.first).days + 1
        self.per_day = df.groupby("date").size()  # sorted by date
        show_days = self.shows.groupby(["date", "name"]).size()
        self.binges = show_days[show_days >= BINGE]
        # df is newest first, so every play except a title's earliest is a rewatch.
        self.rewatch = df.duplicated("title", keep="last")
        self.first_seen = df.groupby(["name", "kind"])["date"].min().reset_index()


def analyse(parsed: Parsed) -> dict:
    h = _History(parsed)
    totals = _totals(h)
    yearly = _yearly(h)
    return {
        "meta": {
            "records": len(h.df),
            "first": h.first.date().isoformat(),
            "last": h.last.date().isoformat(),
            "years": h.years,
            "dateOrder": h.date_order,
        },
        "totals": totals,
        "highlights": _highlights(h, totals, yearly),
        "insights": _insights(h, totals, yearly),
        "yearly": yearly,
        "shows": _deep_dive(h),
        # [year, month, day, weekday, shows, movies] per active date
        "daily": _daily(h.df),
        # [name, kind, year, count], summed client-side for any year range
        "titles": _titles(h.df),
        "history": h.df.assign(date=h.df["date"].dt.strftime("%Y-%m-%d"))[
            ["date", "title", "kind", "name", "season", "episode"]
        ].to_dict("records"),
    }


# ---------------------------------------------------------------- totals


def _totals(h: _History) -> dict:
    n = len(h.df)
    active = len(h.per_day)
    brk = _longest_break(h.per_day.index)
    return {
        "shows": len(h.shows),
        "movies": len(h.movies),
        "distinctShows": int(h.shows["name"].nunique()),
        "distinctMovies": int(h.movies["name"].nunique()),
        "activeDays": active,
        "spanDays": h.span_days,
        "activeShare": _pct(active, h.span_days),
        "avgPerActiveDay": round(n / active, 1),
        "weekendShare": _pct(int((h.df["weekday"] >= 5).sum()), n),
        "longestStreak": _longest_streak(h.per_day.index),
        "longestBreak": brk,
        "bingeSessions": len(h.binges),
        "bingeShare": _pct(int(h.binges.sum()), len(h.shows)),
        "rewatches": int(h.rewatch.sum()),
    }


def _longest_streak(dates: pd.DatetimeIndex) -> int:
    if len(dates) == 0:
        return 0
    run_id = (pd.Series(dates).diff().dt.days != 1).cumsum()
    return int(run_id.value_counts().max())


def _longest_break(dates: pd.DatetimeIndex) -> dict:
    """Longest stretch of days with nothing watched, between two active days."""
    gaps = pd.Series(dates).diff().dt.days
    if len(dates) < 2 or gaps.max() <= 1:
        return {"days": 0, "from": None, "to": None}
    i = int(gaps.idxmax())
    return {
        "days": int(gaps.iloc[i]) - 1,
        "from": (dates[i - 1] + pd.Timedelta(days=1)).date().isoformat(),
        "to": (dates[i] - pd.Timedelta(days=1)).date().isoformat(),
    }


# ---------------------------------------------------------------- per year


def _yearly(h: _History) -> list[dict]:
    df = h.df
    by_kind = df.groupby(["year", "kind"]).size().unstack(fill_value=0)
    by_kind = by_kind.reindex(index=h.years, columns=["show", "movie"], fill_value=0)
    active = df.groupby("year")["date"].nunique()
    distinct = h.shows.groupby("year")["name"].nunique()
    new = (h.first_seen.assign(year=h.first_seen["date"].dt.year)
           .groupby(["year", "kind"]).size().unstack(fill_value=0)
           .reindex(index=h.years, columns=["show", "movie"], fill_value=0))
    return [
        {
            "year": y,
            "shows": int(by_kind.at[y, "show"]),
            "movies": int(by_kind.at[y, "movie"]),
            "activeDays": int(active.get(y, 0)),
            "distinctShows": int(distinct.get(y, 0)),
            "newShows": int(new.at[y, "show"]),
            "newMovies": int(new.at[y, "movie"]),
        }
        for y in h.years
    ]


# ---------------------------------------------------------------- shows


def _deep_dive(h: _History) -> list[dict]:
    if h.shows.empty:
        return []
    g = h.shows.groupby("name")
    table = pd.DataFrame({
        "plays": g.size(),
        "episodes": g["title"].nunique(),
        "seasons": g["season"].nunique(),
        "first": g["date"].min(),
        "last": g["date"].max(),
        "days": g["date"].nunique(),
    }).sort_values(["plays", "days"], ascending=False).head(DEEP_DIVE)
    binges = h.binges.groupby(level="name").size()
    by_year = (h.shows[h.shows["name"].isin(table.index)]
               .groupby(["name", "year"]).size().unstack(fill_value=0)
               .reindex(columns=h.years, fill_value=0))
    return [
        {
            "name": name,
            "plays": int(r.plays),
            "episodes": int(r.episodes),
            "seasons": int(r.seasons),
            "first": r.first.date().isoformat(),
            "last": r.last.date().isoformat(),
            "days": int(r.days),
            "perDay": round(r.plays / r.days, 1),
            "binges": int(binges.get(name, 0)),
            "byYear": [int(v) for v in by_year.loc[name]],
        }
        for name, r in table.iterrows()
    ]


# ---------------------------------------------------------------- highlights


def _highlights(h: _History, t: dict, yearly: list[dict]) -> list[dict]:
    out: list[dict] = []

    def add(key: str, label: str, value: str, sub: str) -> None:
        out.append({"key": key, "label": label, "value": value, "sub": sub})

    def top(series: pd.Series) -> tuple[object, int] | None:
        if series.empty:
            return None
        counts = series.value_counts()
        return counts.index[0], int(counts.iloc[0])

    df = h.df
    if x := top(h.shows["name"]):
        add("topShow", "Top show", x[0], f"{_n(x[1], 'play')}")
    if x := top(h.movies["name"]):
        add("topMovie", "Top movie", x[0], f"{_n(x[1], 'play')}")
    y = max(yearly, key=lambda r: r["shows"] + r["movies"])
    add("busiestYear", "Busiest year", str(y["year"]), f"{y['shows'] + y['movies']:,} watched")
    if x := top(df["month"]):
        add("busiestMonth", "Busiest month", MONTHS[x[0] - 1], f"{x[1]:,} watched")
    if x := top(df["weekday"]):
        add("favouriteWeekday", "Favourite day", WEEKDAYS[x[0]], f"{x[1]:,} watched")
    if x := top(df["day"]):
        add("busiestDayOfMonth", "Busiest date", _ordinal(x[0]), f"of the month · {x[1]:,} watched")
    day = h.per_day.idxmax()
    add("biggestDay", "Biggest day", _day(day), f"{int(h.per_day.max())} watched")
    if not h.binges.empty:
        (date, name), n = h.binges.idxmax(), int(h.binges.max())
        add("biggestBinge", "Biggest binge", name, f"{n} episodes · {_day(date)}")

    add("avgPerDay", "Average day", f"{t['avgPerActiveDay']} titles",
        f"on the {t['activeDays']:,} days you watched")
    add("weekendShare", "Weekends", f"{t['weekendShare']}%", "of everything you watch")
    add("activeShare", "Days active", f"{t['activeShare']}%",
        f"{t['activeDays']:,} of {t['spanDays']:,} days")
    brk = t["longestBreak"]
    if brk["days"]:
        span = f"{_day(pd.Timestamp(brk['from']))} – {_day(pd.Timestamp(brk['to']))}"
        add("longestBreak", "Longest break", _n(brk["days"], "day"), span)
    add("bingeSessions", "Binge sessions", f"{t['bingeSessions']:,}",
        f"days with {BINGE}+ episodes of one show")
    rewatched = df.loc[h.rewatch, "title"].value_counts()
    if not rewatched.empty:
        title, times = rewatched.index[0], int(rewatched.iloc[0]) + 1
        name = df.loc[df["title"] == title, "name"].iloc[0]
        detail = title[len(name) + 2:] if title != name else ""
        add("mostRewatched", "Most rewatched", name,
            _n(times, "time") + (f" · {detail}" if detail else ""))
    seasons = df["month"].map(SEASON_OF_MONTH).value_counts()
    add("favouriteSeason", "Favourite season", str(seasons.index[0]),
        f"{int(seasons.iloc[0]):,} watched")
    first = df.iloc[-1]
    add("firstWatched", "First watched", first["name"], _day(first["date"]))
    return out


# ---------------------------------------------------------------- insights


def _insights(h: _History, t: dict, yearly: list[dict]) -> list[dict]:
    """Plain-English observations, most interesting first."""
    out: list[dict] = []
    df, n = h.df, len(h.df)

    def say(key: str, text: str) -> None:
        out.append({"key": key, "text": text})

    total = {r["year"]: r["shows"] + r["movies"] for r in yearly}
    best = max(total, key=total.get)
    text = f"{best} was your busiest year, with {total[best]:,} things watched"
    if total.get(best - 1):
        text += f", {_change(total[best], total[best - 1])} on {best - 1}"
    say("growth", text + ".")

    days = pd.date_range(h.first, h.last)
    weekend_days = int((days.day_of_week >= 5).sum())
    weekend = int((df["weekday"] >= 5).sum())
    if weekend_days and len(days) - weekend_days and n - weekend:
        ratio = (weekend / weekend_days) / ((n - weekend) / (len(days) - weekend_days))
        pct = round(abs(ratio - 1) * 100)
        more = "more" if ratio >= 1 else "less"
        say("weekend", f"You watch {pct}% {more} per day at weekends than on weekdays.")

    if len(h.shows):
        tv = _pct(len(h.shows), n)
        say("mix", f"{tv}% of what you watch is TV episodes, and {100 - tv}% is movies.")
        top = h.shows["name"].value_counts()
        name, count = top.index[0], int(top.iloc[0])
        say("loyalty", f"{name} alone makes up {_pct(count, len(h.shows))}% of all your episodes.")
        say("binge", f"{t['bingeShare']}% of your episodes were watched in binges of "
            f"{BINGE} or more in a day, across {_n(t['bingeSessions'], 'binge session')}.")

    seasons = df["month"].map(SEASON_OF_MONTH).value_counts()
    if len(seasons) > 1:
        hi, lo = seasons.index[0], seasons.index[-1]
        say("season", f"You watch the most in {hi} and the least in {lo} "
            f"({round((seasons.iloc[0] / seasons.iloc[-1] - 1) * 100)}% more).")

    peak = max(yearly, key=lambda r: r["newShows"])
    if peak["newShows"]:
        say("discovery", f"You discovered the most new shows in {peak['year']} "
            f"({peak['newShows']}), and {_n(yearly[-1]['newShows'], 'new show')} "
            f"so far in {yearly[-1]['year']}.")
    brk = t["longestBreak"]["days"]
    rhythm = f"Your longest run was {_n(t['longestStreak'], 'day')} in a row"
    say("rhythm", rhythm + (f", and your longest break was {_n(brk, 'day')}." if brk else "."))
    if t["rewatches"]:
        say("rewatch", f"{_pct(t['rewatches'], n)}% of your plays were rewatches of "
            "something you'd already seen.")
    return out


# ---------------------------------------------------------------- slices


def _daily(df: pd.DataFrame) -> list[list[int]]:
    g = (df.pivot_table(index="date", columns="kind", values="title", aggfunc="size", fill_value=0)
           .reindex(columns=["show", "movie"], fill_value=0)
           .sort_index())
    idx = g.index
    return [list(map(int, row)) for row in zip(
        idx.year, idx.month, idx.day, idx.day_of_week, g["show"], g["movie"], strict=True)]


def _titles(df: pd.DataFrame) -> list[list]:
    g = df.groupby(["name", "kind", "year"]).size()
    return [[name, kind, int(year), int(c)] for (name, kind, year), c in g.items()]


# ---------------------------------------------------------------- formatting


def _pct(part: int, whole: int) -> int:
    return round(part / whole * 100) if whole else 0


def _n(n: int, word: str) -> str:
    return f"{n:,} {word}{'' if n == 1 else 's'}"


def _change(now: int, before: int) -> str:
    pct = round((now / before - 1) * 100)
    return f"up {pct}%" if pct >= 0 else f"down {-pct}%"


def _day(ts: pd.Timestamp) -> str:
    # "%-d" (no leading zero) is not supported by strftime on Windows.
    return f"{ts.day} {ts:%b %Y}"


def _ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
