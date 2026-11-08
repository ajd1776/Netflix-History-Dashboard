import { useRef, useState, type DragEvent } from 'react'

export function Upload({ onFile, onSample, busy, error }: {
  onFile: (f: File) => void
  onSample: () => void
  busy: boolean
  error: string | null
}) {
  const input = useRef<HTMLInputElement>(null)
  const [over, setOver] = useState(false)

  const drop = (e: DragEvent) => {
    e.preventDefault()
    setOver(false)
    const f = e.dataTransfer.files[0]
    if (f) onFile(f)
  }

  return (
    <main className="upload">
      <div className="upload-hero">
        <img src="/favicon.svg" alt="" width={72} height={72} className="app-icon" />
        <h1>Your Netflix History</h1>
        <p className="lede">See what you've watched, when you watch, and what you keep coming back to.</p>
      </div>

      <section
        className={`glass dropzone ${over ? 'over' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setOver(true) }}
        onDragLeave={() => setOver(false)}
        onDrop={drop}
      >
        <svg width="44" height="44" viewBox="0 0 24 24" aria-hidden className="drop-icon">
          <path d="M12 16V4m0 0-4.5 4.5M12 4l4.5 4.5M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"
            fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        <h2>{busy ? 'Reading your history…' : 'Drop NetflixViewingHistory.csv here'}</h2>
        <p className="sub">It's analysed in memory and never stored.</p>
        <div className="row">
          <button className="btn primary" disabled={busy} onClick={() => input.current?.click()}>
            Choose file
          </button>
          <button className="btn" disabled={busy} onClick={onSample}>Try sample data</button>
        </div>
        <input ref={input} type="file" accept=".csv,text/csv" hidden
          onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); e.target.value = '' }} />
        {error && <p className="error" role="alert">{error}</p>}
      </section>

      <ol className="steps">
        <li className="glass">
          <b>1</b>
          <span>Open <a href="https://www.netflix.com/viewingactivity" target="_blank" rel="noreferrer">
            netflix.com/viewingactivity</a> and pick your profile.</span>
        </li>
        <li className="glass"><b>2</b><span>Scroll to the bottom and choose <em>Download all</em>.</span></li>
        <li className="glass"><b>3</b><span>Drop the CSV above. UK and US date formats both work.</span></li>
      </ol>
    </main>
  )
}
