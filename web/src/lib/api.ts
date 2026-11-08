export type Kind = 'show' | 'movie'

export interface Highlight {
  key: string
  label: string
  value: string
  sub: string
}

export interface Insight {
  key: string
  text: string
}

export interface YearStats {
  year: number
  shows: number
  movies: number
  activeDays: number
  distinctShows: number
  newShows: number
  newMovies: number
}

export interface ShowStats {
  name: string
  plays: number
  episodes: number
  seasons: number
  first: string
  last: string
  days: number
  perDay: number
  binges: number
  /** plays per year, aligned with meta.years */
  byYear: number[]
}

export interface HistoryRow {
  date: string
  title: string
  kind: Kind
  name: string
  season: string
  episode: string
}

/** [year, month 1-12, day, weekday 0=Mon, shows, movies] */
export type DailyRow = [number, number, number, number, number, number]
/** [name, kind, year, count] */
export type TitleRow = [string, Kind, number, number]

export interface Analysis {
  meta: { records: number; first: string; last: string; years: number[]; dateOrder: string }
  totals: {
    shows: number
    movies: number
    distinctShows: number
    distinctMovies: number
    activeDays: number
    spanDays: number
    activeShare: number
    avgPerActiveDay: number
    weekendShare: number
    longestStreak: number
    longestBreak: { days: number; from: string | null; to: string | null }
    bingeSessions: number
    bingeShare: number
    rewatches: number
  }
  highlights: Highlight[]
  insights: Insight[]
  yearly: YearStats[]
  shows: ShowStats[]
  daily: DailyRow[]
  titles: TitleRow[]
  history: HistoryRow[]
}

async function unwrap(res: Response): Promise<Analysis> {
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail ?? `Request failed (${res.status})`)
  }
  return res.json()
}

export const fetchSample = () => fetch('/api/sample').then(unwrap)

export function analyzeFile(file: File) {
  const form = new FormData()
  form.append('file', file)
  return fetch('/api/analyze', { method: 'POST', body: form }).then(unwrap)
}
