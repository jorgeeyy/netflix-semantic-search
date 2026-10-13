import type {
  AskResponse,
  Backend,
  HealthResponse,
  IngestResponse,
  MetaResponse,
  SearchResponse,
} from '../types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(body.detail ?? `Request failed (${res.status})`)
  }
  return res.json() as Promise<T>
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>('/api/health')
}

export function getMeta(): Promise<MetaResponse> {
  return request<MetaResponse>('/api/meta')
}

export function switchBackend(backend: Backend): Promise<MetaResponse> {
  return request<MetaResponse>('/api/backend', {
    method: 'POST',
    body: JSON.stringify({ backend }),
  })
}

export function search(query: string): Promise<SearchResponse> {
  return request<SearchResponse>('/api/search', {
    method: 'POST',
    body: JSON.stringify({ query }),
  })
}

export function ask(question: string): Promise<AskResponse> {
  return request<AskResponse>('/api/ask', {
    method: 'POST',
    body: JSON.stringify({ question }),
  })
}

export function ingest(wipe: boolean, backend: Backend): Promise<IngestResponse> {
  return request<IngestResponse>('/api/ingest', {
    method: 'POST',
    body: JSON.stringify({ wipe, backend }),
  })
}
