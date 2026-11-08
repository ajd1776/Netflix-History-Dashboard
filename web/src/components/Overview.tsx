import { useMemo, useState } from 'react'
import {
  MONTHS, byDayOfMonth, byMonth, byWeekday, calendarYear, filterDaily, fmt, fmtDate, timeline,
  topTitles, totals, weekdayByMonth, type Range,
} from '../lib/aggregate'
import type { Analysis, Insight, Kind, YearStats } from '../lib/api'
import { GlassCard, RangeSlider, Segmented, Stepper } from './Glass'
import { Icon } from './Icon'
import { ShowTable } from './ShowTable'
import { BarChart } from './charts/BarChart'
import { Calendar } from './charts/Calendar'
import { Donut } from './charts/Donut'
import { Matrix } from './charts/Matrix'
import { Timeline } from './charts/Timeline'
import { TopTitles } from './charts/TopTitles'

const KIND_OPTIONS: { value: Kind; label: string }[] = [
  { value: 'show', label: 'Shows' }, { value: 'movie', label: 'Movies' },
]

export function Overview({ data, years }: { data: Analysis; years: Range }) {
  const { meta, totals: t, highlights, insights, yearly, shows, daily, titles, history } = data
  const [months, setMonths] = useState<Range>([1, 12])
  const [kind, setKind] = useState<Kind>('show')
  const [topN, setTopN] = useState(8)
  const [calYear, setCalYear] = useState(meta.years.at(-1)!)
  const [recentKind, setRecentKind] = useState<Kind>('show')

  // Everything below is derived once per change of its inputs, not on every render.
  const months12 = useMemo(() => timeline(daily), [daily])
  const inYears = useMemo(() => filterDaily(daily, years), [daily, years])
  const filtered = useMemo(() => ({
    sum: totals(inYears),
    byMonth: byMonth(inYears),
    byWeekday: byWeekday(inYears),
    grid: weekdayByMonth(inYears),
  }), [inYears])
  const byDay = useMemo(() => byDayOfMonth(filterDaily(daily, years, months)), [daily, years, months])
  const top = useMemo(() => topTitles(titles, kind, years, topN), [titles, kind, years, topN])
  const calendar = useMemo(() => calendarYear(daily, calYear), [daily, calYear])
  const recent = useMemo(() => {
    const seen = new Set<string>()
    return history.filter((h) => h.kind === recentKind && !seen.has(h.name) && seen.add(h.name)).slice(0, 5)
  }, [history, recentKind])

  const span = years[0] === years[1] ? `${years[0]}` : `${years[0]}–${years[1]}`
  const allTime = `All time · ${meta.years[0]}–${meta.years.at(-1)}`
  const monthSpan = months[0] === months[1]
    ? MONTHS[months[0] - 1] : `${MONTHS[months[0] - 1]}–${MONTHS[months[1] - 1]}`
  const calTotal = [...calendar.values()].reduce((a, b) => a + b, 0)

  return (
    <div className="grid">
      <GlassCard className="span-12 hero">
        <div className="hero-head">
          <div>
            <p className="eyebrow">{fmtDate(meta.first)} – {fmtDate(meta.last)}</p>
            <h1><span className="big">{fmt.format(meta.records)}</span> things watched</h1>
          </div>
          <div className="kpis">
            <Kpi label="Episodes" value={fmt.format(t.shows)} sub={`${t.distinctShows} shows`} />
            <Kpi label="Movies" value={fmt.format(t.movies)} sub={`${t.distinctMovies} titles`} />
            <Kpi label="Active days" value={fmt.format(t.activeDays)} sub={`${t.activeShare}% of days`} />
            <Kpi label="Longest streak" value={fmt.format(t.longestStreak)} sub="days in a row" />
          </div>
        </div>
        <Timeline data={months12} range={years} />
        <div className="hero-foot">
          <Legend />
          <span className="legend-trend">3-month average</span>
        </div>
      </GlassCard>

      <div className="span-12 highlights">
        {highlights.map((h) => (
          <div key={h.key} className="glass tile">
            <Icon name={h.key} className="tile-icon" />
            <span className="tile-label">{h.label}</span>
            <span className="tile-value" title={h.value}>{h.value}</span>
            <span className="tile-count" title={h.sub}>{h.sub}</span>
          </div>
        ))}
      </div>

      <GlassCard className="span-5" title="What your history says" subtitle={allTime}>
        <Insights items={insights} />
      </GlassCard>

      <GlassCard className="span-7" title="Year by year" subtitle={allTime} actions={<Legend />}>
        <BarChart data={yearly.map((y) => ({ label: String(y.year), shows: y.shows, movies: y.movies }))}
          height={440} />
        <YearChanges yearly={yearly} />
      </GlassCard>

      <GlassCard className="span-7" title="Monthly activity" subtitle={span} actions={<Legend />}>
        <BarChart data={filtered.byMonth} height={280} />
      </GlassCard>

      <GlassCard className="span-5" title={`Top ${kind === 'show' ? 'shows' : 'movies'}`} subtitle={span}
        actions={<>
          <Stepper label="Titles shown" min={3} max={20} value={topN} onChange={setTopN} />
          <Segmented label="Title type" value={kind} onChange={setKind} options={KIND_OPTIONS} />
        </>}>
        <TopTitles items={top} color={kind === 'show' ? 'var(--show-fill)' : 'var(--movie-fill)'} />
      </GlassCard>

      <GlassCard className="span-6" title="When you watch" subtitle={`${span} · weekday by month`}>
        <Matrix grid={filtered.grid} />
        <HeatKey />
      </GlassCard>

      <GlassCard className="span-3" title="Day of the week" subtitle={span}>
        <BarChart data={filtered.byWeekday} height={320} />
      </GlassCard>

      <GlassCard className="span-3" title="Shows vs movies" subtitle={span}>
        <Donut shows={filtered.sum.shows} movies={filtered.sum.movies} size={190} />
      </GlassCard>

      <GlassCard className="span-6" title="Day of the month" subtitle={`${span} · ${monthSpan}`}>
        <BarChart data={byDay} height={230} tickEvery={3} tooltipLabel={(s) => `Day ${s.label}`} />
        <RangeSlider label="Months" min={1} max={12} value={months} onChange={setMonths}
          format={(m) => MONTHS[m - 1]} />
      </GlassCard>

      <GlassCard className="span-6" title="New titles each year" subtitle="First time you watched a show or movie"
        actions={<Legend shows="New shows" movies="New movies" />}>
        <BarChart data={yearly.map((y) => ({ label: String(y.year), shows: y.newShows, movies: y.newMovies }))}
          height={250} names={{ shows: 'New shows', movies: 'New movies' }} />
      </GlassCard>

      {shows.length > 0 && (
        <GlassCard className="span-12" title="Show deep dive"
          subtitle={`Your ${shows.length} most-watched shows · ${allTime}`}>
          <ShowTable shows={shows} years={meta.years} />
        </GlassCard>
      )}

      <GlassCard className="span-8 calendar-card" title="Viewing calendar"
        subtitle={`${fmt.format(calTotal)} watched in ${calYear}`}
        actions={meta.years.length > 1 && (
          <Segmented label="Calendar year" value={String(calYear)} onChange={(v) => setCalYear(+v)}
            options={meta.years.slice(-5).map((y) => ({ value: String(y), label: String(y) }))} />
        )}>
        <Calendar year={calYear} counts={calendar} />
        <HeatKey />
      </GlassCard>

      <GlassCard className="span-4" title="Recently watched"
        actions={<Segmented label="Recent type" value={recentKind} onChange={setRecentKind} options={KIND_OPTIONS} />}>
        <ul className="recent">
          {recent.map((r) => (
            <li key={r.name}>
              <span className="recent-name">{r.name}</span>
              <span className="recent-meta">{r.season || 'Film'}</span>
              <time>{fmtDate(r.date, true)}</time>
            </li>
          ))}
        </ul>
      </GlassCard>
    </div>
  )
}

function Kpi({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="kpi glass inner">
      <span className="kpi-label">{label}</span>
      <span className="kpi-value">{value}</span>
      {sub && <span className="kpi-sub">{sub}</span>}
    </div>
  )
}

function Legend({ shows = 'Episodes', movies = 'Movies' }: { shows?: string; movies?: string }) {
  return (
    <ul className="legend inline">
      <li><i style={{ background: 'var(--show)' }} />{shows}</li>
      <li><i style={{ background: 'var(--movie)' }} />{movies}</li>
    </ul>
  )
}

function HeatKey() {
  return (
    <div className="heat-key">
      <span>Less</span>{[0, 1, 2, 3, 4].map((l) => <i key={l} className={`heat l${l}`} />)}<span>More</span>
    </div>
  )
}

/** Insight sentences with their numbers picked out. */
function Insights({ items }: { items: Insight[] }) {
  return (
    <ul className="insights">
      {items.map((i) => (
        <li key={i.key}>
          <Icon name={i.key} className="insight-icon" />
          <p>{i.text.split(/(\d+(?:[.,]\d+)*%?)/).map((part, n) => (n % 2 ? <b key={n}>{part}</b> : part))}</p>
        </li>
      ))}
    </ul>
  )
}

/** Each year's total and its change on the year before. */
function YearChanges({ yearly }: { yearly: YearStats[] }) {
  return (
    <div className="yoy" style={{ gridTemplateColumns: `repeat(${yearly.length}, 1fr)` }}>
      {yearly.map((y, i) => {
        const total = y.shows + y.movies
        const prev = i ? yearly[i - 1].shows + yearly[i - 1].movies : 0
        const pct = prev ? Math.round((total / prev - 1) * 100) : null
        return (
          <div key={y.year} className="yoy-cell">
            <span className="yoy-days">{fmt.format(y.activeDays)} days</span>
            {pct === null ? <span className="yoy-change muted">—</span> : (
              <span className={`yoy-change ${pct >= 0 ? 'up' : 'down'}`}>{pct >= 0 ? '▲' : '▼'} {Math.abs(pct)}%</span>
            )}
          </div>
        )
      })}
    </div>
  )
}
