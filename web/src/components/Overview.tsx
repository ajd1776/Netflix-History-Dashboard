import { useMemo, useState } from 'react'
import type { Analysis, Kind } from '../lib/api'
import {
  MONTHS, byDayOfMonth, fmtDate, byMonth, byWeekday, calendarYear, filterDaily, fmt, timeline, topTitles,
  totals, type Range,
} from '../lib/aggregate'
import { GlassCard, RangeSlider, Segmented, Stepper } from './Glass'
import { BarChart } from './charts/BarChart'
import { Calendar } from './charts/Calendar'
import { Donut } from './charts/Donut'
import { Timeline } from './charts/Timeline'
import { TopTitles } from './charts/TopTitles'

// Monochrome line icons, drawn in the accent red.
const ICONS: Record<string, string> = {
  topShow: 'M4 7h16a1 1 0 0 1 1 1v10a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1zM8 3l4 4 4-4',
  topMovie: 'M4 4h16a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V5a1 1 0 0 1 1-1zM3 9h18M8 4 6 9M13 4l-2 5M18 4l-2 5',
  busiestYear: 'M3 17l6-6 4 4 8-8M15 7h6v6',
  busiestMonth: 'M4 5h16a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1zM3 10h18M8 3v4M16 3v4',
  favouriteWeekday: 'M12 3l2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9z',
  busiestDayOfMonth: 'M12 21s-6-5.7-6-11a6 6 0 0 1 12 0c0 5.3-6 11-6 11zM12 8.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z',
  biggestDay: 'M13 2 4 14h7l-1 8 9-12h-7z',
  biggestBinge: 'M12 22c4 0 7-3 7-7 0-4-3-6-4-9-1 2-2 3-4 3 0-2-1-4-2-5 0 4-4 6-4 11 0 4 3 7 7 7z',
}

export function Overview({ data, years }: { data: Analysis; years: Range }) {
  const { meta, totals: t, highlights, daily, titles, history } = data
  const [months, setMonths] = useState<Range>([1, 12])
  const [kind, setKind] = useState<Kind>('show')
  const [topN, setTopN] = useState(8)
  const [calYear, setCalYear] = useState(meta.years.at(-1)!)
  const [recentKind, setRecentKind] = useState<Kind>('show')

  const inYears = useMemo(() => filterDaily(daily, years), [daily, years])
  const inYearsMonths = useMemo(() => filterDaily(daily, years, months), [daily, years, months])
  const sum = totals(inYears)
  const span = years[0] === years[1] ? `${years[0]}` : `${years[0]}–${years[1]}`
  const recent = useMemo(() => {
    const seen = new Set<string>()
    return history.filter((h) => h.kind === recentKind && !seen.has(h.name) && seen.add(h.name)).slice(0, 6)
  }, [history, recentKind])

  return (
    <div className="grid">
      <GlassCard className="span-12 hero">
        <div className="hero-head">
          <div>
            <p className="eyebrow">{fmtDate(meta.first)} – {fmtDate(meta.last)}</p>
            <h1><span className="big">{fmt.format(meta.records)}</span> things watched</h1>
          </div>
          <div className="kpis">
            <Kpi label="Episodes" value={t.shows} sub={`${t.distinctShows} shows`} />
            <Kpi label="Movies" value={t.movies} sub={`${t.distinctMovies} titles`} />
            <Kpi label="Active days" value={t.activeDays} />
            <Kpi label="Longest streak" value={t.longestStreak} sub="days in a row" />
          </div>
        </div>
        <Timeline data={timeline(daily)} />
      </GlassCard>

      <div className="span-12 highlights">
        {highlights.map((h) => (
          <div key={h.key} className="glass tile">
            <svg className="tile-icon" viewBox="0 0 24 24" width="20" height="20" aria-hidden>
              <path d={ICONS[h.key] ?? 'M12 12h0'} />
            </svg>
            <span className="tile-label">{h.label}</span>
            <span className="tile-value" title={h.value}>{h.value}</span>
            <span className="tile-count">{fmt.format(h.count)} {h.key.startsWith('top') || h.key === 'biggestBinge' ? 'plays' : 'watched'}{h.detail ? ` · ${h.detail}` : ''}</span>
          </div>
        ))}
      </div>

      <GlassCard className="span-7" title="Monthly activity" subtitle={span} actions={<Legend />}>
        <BarChart data={byMonth(inYears)} height={280} />
      </GlassCard>

      <GlassCard className="span-5" title={`Top ${kind === 'show' ? 'shows' : 'movies'}`} subtitle={span}
        actions={<Segmented label="Title type" value={kind} onChange={setKind}
          options={[{ value: 'show', label: 'Shows' }, { value: 'movie', label: 'Movies' }]} />}>
        <TopTitles items={topTitles(titles, kind, years, topN)}
          color={kind === 'show' ? 'var(--show-fill)' : 'var(--movie-fill)'} />
        <div className="card-foot">
          <span>Titles shown</span>
          <Stepper label="Titles" min={3} max={20} value={topN} onChange={setTopN} />
        </div>
      </GlassCard>

      <GlassCard className="span-6" title="Day of the month"
        subtitle={`${span} · ${months[0] === months[1] ? MONTHS[months[0] - 1] : `${MONTHS[months[0] - 1]}–${MONTHS[months[1] - 1]}`}`}>
        <BarChart data={byDayOfMonth(inYearsMonths)} height={240} tickEvery={3}
          tooltipLabel={(s) => `Day ${s.label}`} />
        <RangeSlider label="Months" min={1} max={12} value={months} onChange={setMonths}
          format={(m) => MONTHS[m - 1]} />
      </GlassCard>

      <GlassCard className="span-3" title="Day of the week" subtitle={span}>
        <BarChart data={byWeekday(inYears)} height={240} />
      </GlassCard>

      <GlassCard className="span-3" title="Shows vs movies" subtitle={span}>
        <Donut shows={sum.shows} movies={sum.movies} size={170} />
      </GlassCard>

      <GlassCard className="span-8 calendar-card" title="Viewing calendar" subtitle={`${fmt.format(totals(filterDaily(daily, [calYear, calYear])).all)} watched in ${calYear}`}
        actions={meta.years.length > 1 && (
          <Segmented label="Calendar year" value={String(calYear)} onChange={(v) => setCalYear(+v)}
            options={meta.years.slice(-5).map((y) => ({ value: String(y), label: String(y) }))} />
        )}>
        <Calendar year={calYear} counts={calendarYear(daily, calYear)} />
        <div className="heat-key"><span>Less</span>{[0, 1, 2, 3, 4].map((l) => <i key={l} className={`heat l${l}`} />)}<span>More</span></div>
      </GlassCard>

      <GlassCard className="span-4" title="Recently watched"
        actions={<Segmented label="Recent type" value={recentKind} onChange={setRecentKind}
          options={[{ value: 'show', label: 'Shows' }, { value: 'movie', label: 'Movies' }]} />}>
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

function Kpi({ label, value, sub }: { label: string; value: number; sub?: string }) {
  return (
    <div className="kpi glass inner">
      <span className="kpi-label">{label}</span>
      <span className="kpi-value">{fmt.format(value)}</span>
      {sub && <span className="kpi-sub">{sub}</span>}
    </div>
  )
}

function Legend() {
  return (
    <ul className="legend inline">
      <li><i style={{ background: 'var(--show)' }} />Episodes</li>
      <li><i style={{ background: 'var(--movie)' }} />Movies</li>
    </ul>
  )
}
