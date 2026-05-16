// frontend/src/services/inspection.ts
import api from './api'
import { InspectionResult, Defect } from '../types'

export const inspectionApi = {
  inspect: (projectId: string, image: File | string, threshold: number = 0.5) => {
    const formData = new FormData()
    if (typeof image === 'string') {
      return api.post<InspectionResult>('/inspection/single', {
        project_id: projectId,
        image,
        threshold,
      })
    } else {
      formData.append('image', image)
      formData.append('project_id', projectId)
      formData.append('threshold', String(threshold))
      return api.post<InspectionResult>('/inspection/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
    }
  },

  batchInspect: (projectId: string, images: File[]) => {
    const formData = new FormData()
    images.forEach((image) => formData.append('images', image))
    formData.append('project_id', projectId)
    return api.post<{ task_id: string }>('/inspection/batch', formData)
  },

  getResult: (id: string) => api.get<InspectionResult>(`/inspection/${id}`),

  sendFeedback: (inspectionId: string, isCorrect: boolean, correctedDefects?: Defect[], comment?: string) =>
    api.post('/inspection/feedback', {
      inspection_id: inspectionId,
      is_correct: isCorrect,
      corrected_defects: correctedDefects,
      comment,
    }),
}
