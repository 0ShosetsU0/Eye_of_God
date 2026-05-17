// frontend/src/services/inspection.ts
import api from './api'
import { InspectionResult, Defect } from '../types'

export const inspectionApi = {
  inspect: (projectId: string, image: File | string, threshold: number = 0.5) => {
    const formData = new FormData()
    if (typeof image === 'string') {
      return api.post<InspectionResult>('/api/v1/inspection/single', {  // Добавлен /api/v1
        project_id: projectId,
        image,
        threshold,
      })
    } else {
      formData.append('image', image)
      formData.append('project_id', projectId)
      formData.append('threshold', String(threshold))
      return api.post<InspectionResult>('/api/v1/inspection/upload', formData, {  // Добавлен /api/v1
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    }
  },

  batchInspect: (projectId: string, images: File[]) => {
    const formData = new FormData()
    images.forEach((image) => formData.append('images', image))
    formData.append('project_id', projectId)
    return api.post<{ task_id: string }>('/api/v1/inspection/batch', formData)  // Добавлен /api/v1
  },

  getResult: (id: string) => api.get<InspectionResult>(`/api/v1/inspection/${id}`),  // Добавлен /api/v1

  sendFeedback: (inspectionId: string, isCorrect: boolean, correctedDefects?: Defect[], comment?: string) =>
    api.post('/api/v1/inspection/feedback', {  // Добавлен /api/v1
      inspection_id: inspectionId,
      is_correct: isCorrect,
      corrected_defects: correctedDefects,
      comment,
    }),
}