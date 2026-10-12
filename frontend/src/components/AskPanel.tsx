import { useState } from 'react'
import type { FormEvent } from 'react'
import { ask } from '../api/client'
import type { AskResponse } from '../types'

export default function AskPanel() {
  const [question, setQuestion] = useState('')
  const [topK, setTopK] = useState(5)
  const [conversation, setConversation] = useState<AskResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    if (!question.trim()) return
    setLoading(true)
    setError(null)
    try {
      const data = await ask(question, topK)
      setConversation((prev) => [...prev, data])
      setQuestion('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ask failed')
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
          placeholder="Ask a question… e.g. “What are good family documentaries?”"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <select
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
          className="rounded-xl border border-edge bg-input px-3.5 py-3 text-sm text-zinc-100"
        >
          {[3, 5, 10].map((k) => (
            <option key={k} value={k}>
              Context {k}
            </option>
          ))}
        </select>
        <button
          className="cursor-pointer rounded-xl bg-netflix px-6 py-3 text-[0.95rem] font-semibold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          type="submit"
          disabled={loading || !question.trim()}
        >
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </form>

      {error && (
        <div className="mb-4 rounded-xl border border-red-900/50 bg-red-950/40 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="flex flex-col gap-5">
        {conversation.map((entry, i) => (
          <div key={i} className="flex flex-col gap-3">
            <div className="ml-auto max-w-[85%] rounded-xl border border-edge bg-input px-4 py-3.5">
              <span className="mb-1.5 block text-[0.7rem] font-bold uppercase tracking-wide text-zinc-400">
                You
              </span>
              <p className="m-0 whitespace-pre-wrap text-[0.92rem] leading-relaxed">{entry.question}</p>
            </div>
            <div className="max-w-[95%] rounded-xl border border-l-[3px] border-edge border-l-netflix bg-raised px-4 py-3.5">
              <span className="mb-1.5 block text-[0.7rem] font-bold uppercase tracking-wide text-zinc-400">
                Assistant <em className="font-normal normal-case">· {entry.backend}</em>
              </span>
              <p className="m-0 whitespace-pre-wrap text-[0.92rem] leading-relaxed">{entry.answer}</p>
            </div>
            {entry.sources.length > 0 && (
              <details>
                <summary className="cursor-pointer text-sm text-zinc-400">
                  Sources ({entry.sources.length})
                </summary>
                <ul className="mt-2.5 list-disc pl-5 text-sm text-zinc-400">
                  {entry.sources.map((s) => (
                    <li key={s.id} className="mb-2.5">
                      <strong className="text-zinc-200">{s.title || s.id}</strong>
                      {s.director && <> — {s.director}</>}{' '}
                      <span className="font-semibold text-netflix">({Math.round(s.score * 100)}%)</span>
                      {s.description && <p className="mt-1 m-0 text-zinc-500">{s.description}</p>}
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        ))}
        {conversation.length === 0 && !loading && (
          <p className="py-10 text-center text-zinc-400">
            Ask anything about the Netflix dataset to get a grounded answer.
          </p>
        )}
      </div>
    </section>
  )
}
