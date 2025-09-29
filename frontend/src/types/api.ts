export interface Subject {
  id: string
  name: string
  description?: string
  aliases: string[]
  tags: string[]
  created_at: string
  updated_at: string
}

export interface SubjectCreate {
  name: string
  description?: string
  aliases?: string[]
  tags?: string[]
}

export interface SubjectUpdate {
  name?: string
  description?: string
  aliases?: string[]
  tags?: string[]
}

export interface Session {
  id: string
  subject: string
  status: 'created' | 'running' | 'paused' | 'completed' | 'failed'
  config_json: Record<string, any>
  created_at: string
  updated_at: string
}

export interface SessionCreate {
  subject: string
  config_json?: Record<string, any>
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface APIError {
  detail?: string
  error?: string
  [key: string]: any
}
