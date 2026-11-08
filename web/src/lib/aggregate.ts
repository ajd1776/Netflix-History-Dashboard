// The API already did the analysis; these just sum its slices for the current filters.
import type { DailyRow, HistoryRow, Kind, TitleRow } from './api'

export type Range = [number, number]
export interface Split { label: string; shows: number; movies: number }

export const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
export const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const inRange = (v: number, [a, b]: Range) => v >= a && v <= b

export function filterDaily(daily: DailyRow[], years: Range, months: Range = [1, 12]) {
  return daily.filter(([y, m]) => inRange(y, years) && inRange(m, months))
}

function bucket(rows: DailyRow[], labels: string[], key: (r: DailyRow) => number): Split[] {
  const out = labels.map((label) => ({ label, shows: 0, movies: 0 }))
  for (const r of rows) {
    const b = out[key(r)]
    b.shows += r[4]
    b.movies += r[5]
  }
  return out
}

export const byMonth = (rows: DailyRow[]) => bucket(rows, MONTHS, (r) => r[1] - 1)
export const byWeekday = (rows: DailyRow[]) => bucket(rows, WEEKDAYS, (r) => r[3])
export const byDayOfMonth = (rows: DailyRow[]) =>
  bucket(rows, Array.from({ length: 31 }, (_, i) => String(i + 1)), (r) => r[2] - 1)

export function totals(rows: DailyRow[]) {
  let shows = 0
  let movies = 0
  for (const r of rows) {
    shows += r[4]
    movies += r[5]
  }
  return { shows, movies, all: shows + movies }
}

export type MonthPoint = Split & { date: Date; avg: number }

/**
 * One point per calendar month between the first and last record, zeros included,
 * with a centred 3-month average to show the trend.
 */
export function timeline(daily: DailyRow[]): MonthPoint[] {
  if (!daily.length) return []
  const key = (y: number, m: number) => y * 12 + (m - 1)
  const first = key(daily[0][0], daily[0][1])
  const last = key(daily.at(-1)![0], daily.at(-1)![1])
  const points: MonthPoint[] = []
  for (let k = first; k <= last; k++) {
    const y = Math.floor(k / 12)
    const m = k % 12
    points.push({ label: `${MONTHS[m]} ${y}`, date: new Date(y, m, 1), shows: 0, movies: 0, avg: 0 })
  }
  for (const r of daily) {
    const p = points[key(r[0], r[1]) - first]
    p.shows += r[4]
    p.movies += r[5]
  }
  points.forEach((p, i) => {
    const near = points.slice(Math.max(0, i - 1), i + 2)
    p.avg = near.reduce((s, q) => s + q.shows + q.movies, 0) / near.length
  })
  return points
}

/** Plays by weekday (rows, Monday first) and month (columns). */
export function weekdayByMonth(rows: DailyRow[]) {
  const grid = Array.from({ length: 7 }, () => new Array<number>(12).fill(0))
  for (const r of rows) grid[r[3]][r[1] - 1] += r[4] + r[5]
  return grid
}

export function topTitles(titles: TitleRow[], kind: Kind, years: Range, n: number) {
  const sums = new Map<string, number>()
  for (const [name, k, y, c] of titles) {
    if (k === kind && inRange(y, years)) sums.set(name, (sums.get(name) ?? 0) + c)
  }
  return [...sums]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name))
    .slice(0, n)
}

/** Counts per ISO date for one year, for the calendar heatmap. */
export function calendarYear(daily: DailyRow[], year: number) {
  const map = new Map<string, number>()
  for (const r of daily) {
    if (r[0] !== year) continue
    map.set(`${r[0]}-${pad(r[1])}-${pad(r[2])}`, r[4] + r[5])
  }
  return map
}

export const pad = (n: number) => String(n).padStart(2, '0')

export function toCsv(rows: HistoryRow[]) {
  const cols: (keyof HistoryRow)[] = ['date', 'title', 'kind', 'name', 'season', 'episode']
  const esc = (v: string) => (/[",\n]/.test(v) ? `"${v.replaceAll('"', '""')}"` : v)
  return [cols.join(','), ...rows.map((r) => cols.map((c) => esc(String(r[c]))).join(','))].join('\n')
}

export const fmt = new Intl.NumberFormat()

export function fmtDate(iso: string, short = false) {
  return new Date(`${iso}T00:00`).toLocaleDateString(undefined,
    short ? { day: 'numeric', month: 'short' } : { day: 'numeric', month: 'short', year: 'numeric' })
}
