import { useEffect, useState } from 'react'
import { getMeta, switchBackend } from './api/client'
import IngestPanel from './components/IngestPanel'
import SearchPanel from './components/SearchPanel'
import type { Backend, MetaResponse } from './types'

type Tab = 'search' | 'ingest'

const TABS: { id: Tab; label: string }[] = [
  { id: 'search', label: 'Search' },
  { id: 'ingest', label: 'Data' },
]

export default function App() {
  const [tab, setTab] = useState<Tab>('search')
  const [meta, setMeta] = useState<MetaResponse | null>(null)
  const [backend, setBackend] = useState<Backend>('pinecone')

  useEffect(() => {
    getMeta()
      .then((m) => {
        setMeta(m)
        setBackend(m.active as Backend)
      })
      .catch(() => setMeta(null))
  }, [])

  async function onSelectBackend(next: Backend) {
    setBackend(next)
    try {
      const m = await switchBackend(next)
      setMeta(m)
    } catch {
      // keep optimistic selection; backend will fall back on next meta fetch
    }
  }

  return (
    <div className="mx-auto min-h-screen max-w-3xl px-5 pb-10">
      <header className="pt-8 mb-7">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Netflix Semantic Search</h1>
            <p className="mt-1.5 text-sm text-zinc-400">
              {meta
                ? `${meta.embedding_model} · ${meta.embedding_dim}-dim · LLM: ${meta.llm_provider}`
                : 'FastAPI · Pinecone / Chroma · OpenAI embeddings'}
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm text-zinc-400">
            <label htmlFor="backend-select">Backend</label>
            <select
              id="backend-select"
              value={backend}
              onChange={(e) => onSelectBackend(e.target.value as Backend)}
              className="rounded-xl border border-edge bg-input px-3.5 py-2.5 text-sm text-zinc-100"
            >
              <option value="pinecone">Pinecone</option>
              <option value="chroma">Chroma</option>
            </select>
          </div>
        </div>
        <nav className="mt-6 flex gap-1 border-b border-edge">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`cursor-pointer border-b-2 px-4 py-2.5 text-[0.95rem] transition-colors ${
                tab === t.id
                  ? 'border-netflix font-semibold text-zinc-100'
                  : 'border-transparent text-zinc-400 hover:text-zinc-100'
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>

      <main>
        {tab === 'search' && <SearchPanel />}
        {tab === 'ingest' && <IngestPanel backend={backend} />}
      </main>

      <footer className="mt-12 text-center text-xs text-zinc-500">
        API docs at{' '}
        <a href="http://localhost:8000/docs" className="text-zinc-400 hover:text-zinc-200">
          localhost:8000/docs
        </a>
      </footer>
    </div>
  )
}
