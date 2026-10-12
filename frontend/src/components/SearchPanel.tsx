import { useState } from 'react'
import type { FormEvent } from 'react'
import { search } from '../api/client'
import type { SearchResult } from '../types'
import ResultCard from './ResultCard'

export default function SearchPanel() {
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(5)
  const [results, setResults] = useState<SearchResult[]>([])
  const [backend, setBackend] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError(null)
    try {
      const data = await search(query, topK)
      setResults(data.results)
      setBackend(data.backend)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <form className="mb-5 flex flex-wrap gap-2.5" onSubmit={onSubmit}>
        <input
          className="min-w-60 flex-1 rounded-xl border border-edge bg-input px-4 py-3 text-[0.95rem] text-zinc-100 placeholder:text-zinc-500 focus:border-netflix focus:outline-none"
          type="text"
          placeholder="Describe what you're looking for… e.g. “a thriller about a home invasion”"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <select
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
          className="rounded-xl border border-edge bg-input px-3.5 py-3 text-sm text-zinc-100"
        >
          {[3, 5, 10, 15].map((k) => (
            <option key={k} value={k}>
              Top {k}
            </option>
          ))}
        </select>
        <button
          className="cursor-pointer rounded-xl bg-netflix px-6 py-3 text-[0.95rem] font-semibold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          type="submit"
          disabled={loading || !query.trim()}
        >
          {loading ? 'Searching…' : 'Search'}
        </button>
      </form>

      {error && (
        <div className="mb-4 rounded-xl border border-red-900/50 bg-red-950/40 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {results.length > 0 && (
        <p className="mb-3.5 text-sm text-zinc-400">
          {results.length} result{results.length !== 1 && 's'} · backend: <strong>{backend}</strong>
        </p>
      )}

      <div className="flex flex-col gap-3.5">
        {results.map((r) => (
          <ResultCard key={r.id} result={r} />
        ))}
      </div>
    </section>
  )
}
