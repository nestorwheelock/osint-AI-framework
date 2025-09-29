import axios, { AxiosResponse } from 'axios'
import { Subject, SubjectCreate, SubjectUpdate, Session, SessionCreate, PaginatedResponse, APIError } from '../types/api'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth (when we add authentication)
api.interceptors.request.use(
  (config) => {
    // Add auth token when available
    // const token = localStorage.getItem('auth_token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const errorMessage = error.response?.data?.detail ||
                        error.response?.data?.error ||
                        error.message ||
                        'An unexpected error occurred'

    throw new Error(errorMessage)
  }
)

// Subject API methods
export const subjectAPI = {
  list: async (page = 1, limit = 20): Promise<PaginatedResponse<Subject>> => {
    const response: AxiosResponse<PaginatedResponse<Subject>> = await api.get(
      `/api/subjects/?page=${page}&limit=${limit}`
    )
    return response.data
  },

  get: async (id: string): Promise<Subject> => {
    const response: AxiosResponse<Subject> = await api.get(`/api/subjects/${id}/`)
    return response.data
  },

  create: async (data: SubjectCreate): Promise<Subject> => {
    const response: AxiosResponse<Subject> = await api.post('/api/subjects/', data)
    return response.data
  },

  update: async (id: string, data: SubjectUpdate): Promise<Subject> => {
    const response: AxiosResponse<Subject> = await api.patch(`/api/subjects/${id}/`, data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/subjects/${id}/`)
  },
}

// Session API methods
export const sessionAPI = {
  list: async (page = 1, limit = 20): Promise<PaginatedResponse<Session>> => {
    const response: AxiosResponse<PaginatedResponse<Session>> = await api.get(
      `/api/sessions/?page=${page}&limit=${limit}`
    )
    return response.data
  },

  get: async (id: string): Promise<Session> => {
    const response: AxiosResponse<Session> = await api.get(`/api/sessions/${id}/`)
    return response.data
  },

  create: async (data: SessionCreate): Promise<Session> => {
    const response: AxiosResponse<Session> = await api.post('/api/sessions/', data)
    return response.data
  },

  updateStatus: async (id: string, status: Session['status']): Promise<Session> => {
    const response: AxiosResponse<Session> = await api.patch(`/api/sessions/${id}/`, { status })
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/sessions/${id}/`)
  },
}

export default api
