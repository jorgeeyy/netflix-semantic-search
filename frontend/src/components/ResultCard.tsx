import type { SearchResult } from '../types'

export default function ResultCard({ result }: { result: SearchResult }) {
  const percent = Math.round(result.score * 100)
  return (
    <article className="rounded-xl border border-edge bg-raised p-5">
      <div className="flex items-baseline justify-between gap-3">
        <h3 className="text-[1.05rem] font-semibold">{result.title || 'Untitled'}</h3>
        <span className="text-sm font-bold text-netflix" title={`Similarity score: ${result.score.toFixed(3)}`}>
          {percent}%
        </span>
      </div>
      <div className="mt-2.5 mb-3 h-1 overflow-hidden rounded-full bg-input">
        <div className="h-full rounded-full bg-netflix" style={{ width: `${percent}%` }} />
      </div>
      <div className="mb-2.5 flex flex-wrap gap-1.5">
        {result.type && (
          <span className="rounded-full bg-red-950/50 px-2.5 py-0.5 text-xs font-semibold text-netflix">
            {result.type}
          </span>
        )}
        {result.genres &&
          result.genres
            .split(',')
            .slice(0, 3)
            .map((g) => (
              <span key={g} className="rounded-full bg-input px-2.5 py-0.5 text-xs text-zinc-400">
                {g.trim()}
              </span>
            ))}
        {result.release_year && (
          <span className="rounded-full bg-input px-2.5 py-0.5 text-xs text-zinc-400">{result.release_year}</span>
        )}
        {result.rating && (
          <span className="rounded-full bg-input px-2.5 py-0.5 text-xs text-zinc-400">{result.rating}</span>
        )}
      </div>
      {result.director && <p className="mb-1.5 text-sm text-zinc-400">Directed by {result.director}</p>}
      {result.description && <p className="text-sm leading-relaxed text-zinc-200">{result.description}</p>}
    </article>
  )
}
