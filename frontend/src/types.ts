export interface SearchResult {
  id: string
  score: number
  title: string
  type: string
  director: string
  cast: string
  country: string
  release_year: string
  rating: string
  duration: string
  genres: string
  description: string
}

export interface SearchResponse {
  query: string
  backend: string
  results: SearchResult[]
}

export interface Source {
  id: string
  score: number
  title: string
  director: string
  genres: string
  description: string
}

export interface AskResponse {
  question: string
  answer: string
  sources: Source[]
  backend: string
}

export interface IngestResponse {
  status: string
  count: number
  backend: string
  elapsed_seconds: number
}

export interface HealthResponse {
  status: string
  backend: string
  vector_count: number | null
}

export interface MetaResponse {
  backends: string[]
  active: string
  embedding_model: string
  embedding_dim: number
  llm_provider: string
  csv_path: string
}

export type Backend = 'pinecone' | 'chroma'
