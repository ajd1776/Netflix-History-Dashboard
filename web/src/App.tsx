import { useState } from 'react'
import { History } from './components/History'
import { Overview } from './components/Overview'
import { RangeSlider, Segmented } from './components/Glass'
import { Upload } from './components/Upload'
import { analyzeFile, fetchSample, type Analysis } from './lib/api'
import type { Range } from './lib/aggregate'

type Tab = 'overview' | 'history'

export default function App() {
  const [data, setData] = useState<Analysis | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [tab, setTab] = useState<Tab>('overview')
  const [years, setYears] = useState<Range>([0, 0])

  const load = async (p: Promise<Analysis>) => {
    setBusy(true)
    setError(null)
    try {
      const d = await p
      setData(d)
      setYears([d.meta.years[0], d.meta.years.at(-1)!])
      setTab('overview')
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setBusy(false)
    }
  }

  return (
    <>
      <div className="backdrop" aria-hidden><i /><i /></div>
      {!data ? (
        <Upload busy={busy} error={error} onSample={() => load(fetchSample())}
          onFile={(f) => load(analyzeFile(f))} />
      ) : (
        <>
          <header className="glass navbar">
            <div className="brand">
              <img src="/favicon.svg" alt="" width={28} height={28} />
              <span>Netflix History</span>
            </div>
            <Segmented label="Section" value={tab} onChange={setTab}
              options={[{ value: 'overview', label: 'Overview' }, { value: 'history', label: 'History' }]} />
            <div className="nav-right">
              {tab === 'overview' && data.meta.years.length > 1 && (
                <div className="year-filter">
                  <span className="filter-label">
                    Years <b>{years[0] === years[1] ? years[0] : `${years[0]}–${years[1]}`}</b>
                  </span>
                  <RangeSlider label="Years" min={data.meta.years[0]} max={data.meta.years.at(-1)!}
                    value={years} onChange={setYears} />
                </div>
              )}
              <button className="btn" onClick={() => setData(null)}>New file</button>
            </div>
          </header>
          <main className="dashboard">
            {tab === 'overview' ? <Overview data={data} years={years} /> : <History rows={data.history} />}
          </main>
        </>
      )}
    </>
  )
}
