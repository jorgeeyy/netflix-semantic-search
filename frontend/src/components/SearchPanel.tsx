import { useState } from 'react'
import type { FormEvent } from 'react'
import { ask, search } from '../api/client'
import type { SearchResult } from '../types'
import ResultCard from './ResultCard'

export default function SearchPanel() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [answer, setAnswer] = useState<string | null>(null)
  const [backend, setBackend] = useState('')
  const [loading, setLoading] = useState<'search' | 'ask' | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function onSearch(e: FormEvent) {
    e.preventDefault()
    if (!query.trim()) return
    setLoading('search')
    setError(null)
    setAnswer(null)
    try {
      const data = await search(query)
      setResults(data.results)
      setBackend(data.backend)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
      setResults([])
    } finally {
      setLoading(null)
    }
  }

  async function onAsk() {
    if (!query.trim()) return
    setLoading('ask')
    setError(null)
    setResults([])
    try {
      const data = await ask(query)
      setAnswer(data.answer)
      setBackend(data.backend)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ask failed')
      setAnswer(null)
    } finally {
      setLoading(null)
    }
  }

  return (
    <section>
      <form className="mb-5 flex flex-wrap gap-2.5" onSubmit={onSearch}>
        <input
          className="min-w-60 flex-1 rounded-xl border border-edge bg-input px-4 py-3 text-[0.95rem] text-zinc-100 placeholder:text-zinc-500 focus:border-netflix focus:outline-none"
          type="text"
          placeholder="e.g. “who directed ganglands” or “top three home invasion movies”"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          className="cursor-pointer rounded-xl bg-netflix px-6 py-3 text-[0.95rem] font-semibold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          type="submit"
          disabled={loading !== null || !query.trim()}
        >
          {loading === 'search' ? 'Searching…' : 'Search'}
        </button>
        <button
          className="cursor-pointer rounded-xl border border-edge px-6 py-3 text-[0.95rem] font-semibold text-zinc-300 transition-colors hover:border-zinc-500 hover:text-zinc-100 disabled:cursor-not-allowed disabled:opacity-50"
          type="button"
          onClick={onAsk}
          disabled={loading !== null || !query.trim()}
        >
          {loading === 'ask' ? 'Thinking…' : 'Ask AI'}
        </button>
      </form>

      {error && (
        <div className="mb-4 rounded-xl border border-red-900/50 bg-red-950/40 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      {answer !== null && (
        <div className="mb-5 max-w-[95%] rounded-xl border border-l-[3px] border-edge border-l-netflix bg-raised px-4 py-3.5">
          <span className="mb-1.5 block text-[0.7rem] font-bold uppercase tracking-wide text-zinc-400">
            AI answer <em className="font-normal normal-case">· {backend}</em>
          </span>
          <p className="m-0 whitespace-pre-wrap text-base font-semibold leading-relaxed">{answer}</p>
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
