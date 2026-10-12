import { useState } from 'react'
import { getHealth, ingest } from '../api/client'
import type { Backend, HealthResponse, IngestResponse } from '../types'

interface Props {
  backend: Backend
}

export default function IngestPanel({ backend }: Props) {
  const [wipe, setWipe] = useState(false)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState<IngestResponse | null>(null)
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function refreshHealth() {
    try {
      setHealth(await getHealth())
    } catch {
      setHealth(null)
    }
  }

  async function runIngest() {
    setBusy(true)
    setError(null)
    setResult(null)
    try {
      const data = await ingest(wipe, backend)
      setResult(data)
      await refreshHealth()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ingest failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section>
      <div className="rounded-xl border border-edge bg-raised p-6">
        <h2 className="m-0 text-lg font-semibold">Ingest dataset</h2>
        <p className="mb-4 mt-2 text-sm leading-relaxed text-zinc-400">
          Re-embed <code className="rounded-md bg-input px-1.5 py-0.5 text-[0.85em]">netflix_titles_1000.csv</code>{' '}
          ({backend}) with{' '}
          <code className="rounded-md bg-input px-1.5 py-0.5 text-[0.85em]">text-embedding-3-small</code>. Takes
          ~20–60s for 1000 records.
        </p>
        <label className="mb-4 flex cursor-pointer items-center gap-2 text-sm text-zinc-400">
          <input
            type="checkbox"
            checked={wipe}
            onChange={(e) => setWipe(e.target.checked)}
            className="accent-[#e50914]"
          />
          Wipe existing vectors first
        </label>
        <div className="flex flex-wrap gap-2.5">
          <button
            onClick={runIngest}
            disabled={busy}
            className="cursor-pointer rounded-xl bg-netflix px-6 py-3 text-sm font-semibold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {busy ? 'Ingesting…' : wipe ? 'Wipe & re-ingest' : 'Ingest'}
          </button>
          <button
            onClick={refreshHealth}
            disabled={busy}
            className="cursor-pointer rounded-xl border border-edge px-6 py-3 text-sm font-semibold text-zinc-400 transition-colors hover:border-zinc-500 hover:text-zinc-100 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Check vector count
          </button>
        </div>

        {error && (
          <div className="mt-4 rounded-xl border border-red-900/50 bg-red-950/40 px-4 py-3 text-sm text-red-400">
            {error}
          </div>
        )}
        {result && (
          <div className="mt-4 rounded-xl border border-emerald-900/50 bg-emerald-950/40 px-4 py-3 text-sm text-emerald-400">
            Ingested <strong>{result.count}</strong> records into <strong>{result.backend}</strong> in{' '}
            {result.elapsed_seconds}s.
          </div>
        )}
        {health && (
          <p className="mt-4 text-sm text-zinc-400">
            Current: backend <strong>{health.backend}</strong> ·{' '}
            {health.vector_count != null ? `${health.vector_count} vectors` : 'count unavailable'}
          </p>
        )}
      </div>
    </section>
  )
}
