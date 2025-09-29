import React, { createContext, useContext, ReactNode } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { subjectAPI, sessionAPI } from '../services/api'
import { Subject, SubjectCreate, SubjectUpdate, Session, SessionCreate } from '../types/api'

interface APIContextType {
  // Subject queries and mutations
  subjects: {
    list: ReturnType<typeof useQuery>
    create: ReturnType<typeof useMutation>
    update: ReturnType<typeof useMutation>
    delete: ReturnType<typeof useMutation>
  }
  // Session queries and mutations
  sessions: {
    list: ReturnType<typeof useQuery>
    create: ReturnType<typeof useMutation>
    updateStatus: ReturnType<typeof useMutation>
    delete: ReturnType<typeof useMutation>
  }
}

const APIContext = createContext<APIContextType | undefined>(undefined)

export function APIProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()

  // Subject queries and mutations
  const subjectsList = useQuery({
    queryKey: ['subjects'],
    queryFn: () => subjectAPI.list(),
  })

  const createSubject = useMutation({
    mutationFn: (data: SubjectCreate) => subjectAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] })
    },
  })

  const updateSubject = useMutation({
    mutationFn: ({ id, data }: { id: string; data: SubjectUpdate }) =>
      subjectAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] })
    },
  })

  const deleteSubject = useMutation({
    mutationFn: (id: string) => subjectAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['subjects'] })
    },
  })

  // Session queries and mutations
  const sessionsList = useQuery({
    queryKey: ['sessions'],
    queryFn: () => sessionAPI.list(),
  })

  const createSession = useMutation({
    mutationFn: (data: SessionCreate) => sessionAPI.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
    },
  })

  const updateSessionStatus = useMutation({
    mutationFn: ({ id, status }: { id: string; status: Session['status'] }) =>
      sessionAPI.updateStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
    },
  })

  const deleteSession = useMutation({
    mutationFn: (id: string) => sessionAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['sessions'] })
    },
  })

  const contextValue: APIContextType = {
    subjects: {
      list: subjectsList,
      create: createSubject,
      update: updateSubject,
      delete: deleteSubject,
    },
    sessions: {
      list: sessionsList,
      create: createSession,
      updateStatus: updateSessionStatus,
      delete: deleteSession,
    },
  }

  return (
    <APIContext.Provider value={contextValue}>
      {children}
    </APIContext.Provider>
  )
}

export function useAPI() {
  const context = useContext(APIContext)
  if (context === undefined) {
    throw new Error('useAPI must be used within an APIProvider')
  }
  return context
}
