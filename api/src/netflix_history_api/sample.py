"""Made-up viewing history for the demo, in Netflix's UK export format.

It behaves like a real viewer: new shows start over time, episodes are
watched in order (sometimes several at once), favourites get rewatched,
and most movies are seen once.
"""

from __future__ import annotations

import csv
import io
import random
from datetime import date, timedelta

# (name, seasons, episodes per season)
SHOWS = [
    ("Harbour Lights", 4, 10), ("The Quiet Orbit", 3, 8), ("Copper & Coal", 5, 10),
    ("Midnight Bakery", 2, 8), ("Signal Lost", 3, 10), ("Northbound", 1, 6),
    ("The Glass Archive", 2, 9), ("Wild Kitchens", 4, 6), ("Paper Crowns", 2, 10),
    ("Deep Current", 1, 8), ("Lantern Street", 3, 8), ("Saltmarsh", 2, 6),
    ("Velvet Static", 2, 10), ("The Long Field", 3, 6), ("Ember & Ash", 2, 8),
    ("Offshore", 1, 10), ("Kingfisher", 3, 10), ("The Understudy", 2, 6),
    ("Hollow Pines", 2, 8), ("Night Shift Diaries", 4, 8), ("Brightwater", 1, 8),
    ("Station Eleven Road", 2, 10), ("The Cartel Club", 3, 8), ("Small Hours", 2, 6),
]
EPISODES = ["Arrival", "Fault Lines", "The Offer", "Low Tide", "Crossroads", "Smoke",
            "Homecoming", "Ledger", "Old Friends", "Blackout", "The Visit", "Overtime",
            "Undertow", "Stormfront", "Reckoning", "Finale", "First Light", "Static",
            "The Long Night", "Echoes", "Breakwater", "Paper Trail", "Ghosts", "Embers"]
MOVIE_A = ["The Silver", "Last", "Iron", "Saltwater", "Echo", "Static", "The Ninth", "Hollow",
           "Neon", "Paper", "Midnight", "Crimson", "The Quiet", "Broken", "Golden"]
MOVIE_B = ["Harbour", "Train to Arden", "Meadow", "Summer", "Valley", "Hearts", "Lantern",
           "Bay", "Orchard", "Kingdom", "Signal", "Frontier", "Garden", "Season", "Mile"]


def sample_csv(
    seed: int = 42, start: date = date(2019, 3, 1), end: date = date(2025, 10, 31)
) -> bytes:
    rng = random.Random(seed)
    span = (end - start).days

    # Each show turns up on a different day; a few are there from the start.
    step = span // (len(SHOWS) - 3)
    debut = {name: (rng.randint(0, 20) if i < 4 else (i - 3) * step + rng.randint(-40, 40))
             for i, (name, *_) in enumerate(SHOWS)}
    size = {name: (seasons + 2, eps + 6) for name, seasons, eps in SHOWS}
    appeal = {name: rng.uniform(0.4, 3.0) for name, *_ in SHOWS}
    progress: dict[str, tuple[int, int]] = {}  # name -> next (season, episode)
    finished: set[str] = set()
    rewatched: set[str] = set()

    movies = sorted({f"{a} {b}" for a in MOVIE_A for b in MOVIE_B})
    rng.shuffle(movies)
    movies = movies[:70] + ["Operation: Glasshouse"]
    seen: list[str] = []

    rows: list[tuple[str, date]] = []
    for offset in range(span + 1):
        d = start + timedelta(days=offset)
        weekend = d.weekday() >= 5
        winter = d.month in (11, 12, 1, 2)
        if rng.random() > 0.5 + 0.22 * weekend + 0.1 * winter:
            continue

        watching = [s for s in debut if debut[s] <= offset and s not in finished]
        if watching and rng.random() < 0.9:
            show = rng.choices(watching, [appeal[s] for s in watching])[0]
            season, ep = progress.get(show, (1, 1))
            count = rng.choice([1, 1, 1, 2, 2, 3, 4, 5, 6] if weekend else [1, 1, 2, 2, 3])
            for _ in range(count):
                name = EPISODES[(season * 7 + ep * 3) % len(EPISODES)]
                rows.append((f"{show}: Season {season}: {name} (Episode {ep})", d))
                seasons, eps = size[show]
                season, ep = (season, ep + 1) if ep < eps else (season + 1, 1)
                if season > seasons:
                    # Favourites sometimes get a full rewatch later on.
                    if show not in rewatched and appeal[show] > 2.5 and rng.random() < 0.6:
                        rewatched.add(show)
                        season, ep = 1, 1
                        debut[show] = offset + rng.randint(90, 300)
                    else:
                        finished.add(show)
                    break
            progress[show] = (season, ep)

        if rng.random() < (0.3 if weekend else 0.12):
            fresh = [m for m in movies if m not in seen]
            again = not fresh or rng.random() > 0.85
            movie = rng.choice(sorted(set(seen)) or movies) if again else rng.choice(fresh)
            seen.append(movie)
            rows.append((movie, d))

    rows.sort(key=lambda r: r[1], reverse=True)
    buf = io.StringIO()
    buf.write("Title,Date\n")
    writer = csv.writer(buf, quoting=csv.QUOTE_ALL)
    writer.writerows((title, day.strftime("%d/%m/%Y")) for title, day in rows)
    return buf.getvalue().encode()
