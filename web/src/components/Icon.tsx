// Monochrome line icons (24×24, stroked), keyed by highlight and insight keys.
const PATHS: Record<string, string> = {
  topShow: 'M4 7h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1zM8 3l4 4 4-4',
  topMovie: 'M4 4h16a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1zM3 9h18M8 4 6 9M13 4l-2 5M18 4l-2 5',
  busiestYear: 'M3 17l6-6 4 4 8-8M15 7h6v6',
  busiestMonth: 'M4 5h16a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zM3 10h18M8 3v4M16 3v4',
  favouriteWeekday: 'M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z',
  busiestDayOfMonth: 'M12 21s-6-5.7-6-11a6 6 0 0 1 12 0c0 5.3-6 11-6 11zM12 8.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z',
  biggestDay: 'M13 2 4 14h7l-1 8 9-12h-7z',
  biggestBinge: 'M12 22c4 0 7-3 7-7 0-4-3-6-4-9-1 2-2 3-4 3 0-2-1-4-2-5 0 4-4 6-4 11 0 4 3 7 7 7z',
  avgPerDay: 'M12 14l4-4M3.5 18a9 9 0 1 1 17 0',
  weekendShare: 'M4 11V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v3M2 13a2 2 0 0 1 4 0v2h12v-2a2 2 0 0 1 4 0v5H2zM5 18v2M19 18v2',
  activeShare: 'M9 12l2 2 4-4M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18z',
  longestBreak: 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18zM10 9v6M14 9v6',
  bingeSessions: 'M12 2 2 7l10 5 10-5zM2 12l10 5 10-5M2 17l10 5 10-5',
  mostRewatched: 'M17 2l4 4-4 4M3 11V9a3 3 0 0 1 3-3h15M7 22l-4-4 4-4M21 13v2a3 3 0 0 1-3 3H3',
  favouriteSeason: 'M12 17a5 5 0 1 0 0-10 5 5 0 0 0 0 10zM12 1v2M12 21v2M4.2 4.2l1.4 1.4M18.4 18.4l1.4 1.4M1 12h2M21 12h2M4.2 19.8l1.4-1.4M18.4 5.6l1.4-1.4',
  firstWatched: 'M4 22V4M4 4h13l-2 4 2 4H4',
  mix: 'M21 12a9 9 0 1 1-9-9v9zM15 2.5a9 9 0 0 1 6.5 6.5H15z',
  loyalty: 'M12 21s-7-4.4-9.5-9A5.5 5.5 0 0 1 12 6a5.5 5.5 0 0 1 9.5 6c-2.5 4.6-9.5 9-9.5 9z',
  discovery: 'M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8zM19 17l.7 1.8 1.8.7-1.8.7L19 22l-.7-1.8-1.8-.7 1.8-.7z',
  rhythm: 'M3 12h4l3-8 4 16 3-8h4',
}
const ALIASES: Record<string, string> = {
  growth: 'busiestYear', weekend: 'weekendShare', binge: 'biggestBinge',
  season: 'favouriteSeason', rewatch: 'mostRewatched',
}

export function Icon({ name, className = 'icon' }: { name: string; className?: string }) {
  const d = PATHS[name] ?? PATHS[ALIASES[name]] ?? 'M12 12h0'
  return (
    <svg className={className} viewBox="0 0 24 24" width="20" height="20" aria-hidden>
      <path d={d} />
    </svg>
  )
}
