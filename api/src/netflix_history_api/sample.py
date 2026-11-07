"""Made-up viewing history for the demo, in Netflix's UK export format."""

from __future__ import annotations

import csv
import io
import random
from datetime import date, timedelta

SHOWS = {"Harbour Lights": 3, "The Quiet Orbit": 2, "Copper & Coal": 4, "Midnight Bakery": 2,
         "Signal Lost": 3, "Northbound": 1, "The Glass Archive": 2, "Wild Kitchens": 3,
         "Paper Crowns": 2, "Deep Current": 1, "Lantern Street": 2, "Saltmarsh": 1}
WEIGHTS = [9, 7, 6, 5, 4, 3, 3, 2, 2, 1, 2, 1]
MOVIES = ["Last Train to Arden", "The Cartographer", "Iron Meadow", "Saltwater Summer",
          "Echo Valley", "A Winter in Lyon", "Static Hearts", "The Ninth Lantern",
          "Dust & Daylight", "Overcast", "Hollow Bay", "Neon Orchard", "The Long Way Round",
          "Tidewater", "Brass Monkeys", "Operation: Glasshouse"]
EPISODES = ["Arrival", "Fault Lines", "The Offer", "Low Tide", "Crossroads", "Smoke",
            "Homecoming", "Ledger", "Old Friends", "Blackout", "The Visit", "Overtime",
            "Undertow", "Stormfront", "Reckoning", "Finale"]


def sample_csv(
    seed: int = 42, start: date = date(2019, 3, 1), end: date = date(2025, 10, 31)
) -> bytes:
    rng = random.Random(seed)
    rows: list[tuple[str, date]] = []
    d = start
    while d <= end:
        p = 0.5 + (0.25 if d.weekday() >= 4 else 0) + (0.12 if d.month in (12, 1, 2) else 0)
        if rng.random() < p:
            for _ in range(rng.choice([1, 1, 2, 2, 3, 4, 6])):
                if rng.random() < 0.82:
                    show = rng.choices(list(SHOWS), WEIGHTS)[0]
                    season = rng.randint(1, SHOWS[show])
                    ep = f"{rng.choice(EPISODES)} (Episode {rng.randint(1, 10)})"
                    rows.append((f"{show}: Season {season}: {ep}", d))
                else:
                    rows.append((rng.choice(MOVIES), d))
        d += timedelta(days=1)

    rows.sort(key=lambda r: r[1], reverse=True)
    buf = io.StringIO()
    buf.write("Title,Date\n")
    writer = csv.writer(buf, quoting=csv.QUOTE_ALL)
    writer.writerows((title, day.strftime("%d/%m/%Y")) for title, day in rows)
    return buf.getvalue().encode()
