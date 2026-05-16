// frontend/src/services/training.ts
import api from './api'
import { TrainingTask, TrainingConfig } from '../types'

export const trainingApi = {
  start: (projectId: string, config: TrainingConfig) =>
    api.post<{ task_id: string }>('/training/start', {
      project_id: projectId,
      config,
    }),

  getStatus: (taskId: string) =>
    api.get<TrainingTask>(`/training/status/${taskId}`),

  cancel: (taskId: string) =>
    api.post(`/training/cancel/${taskId}`),

  getModels: (projectId: string) =>
    api.get('/models', { params: { project_id: projectId } }),

  activateModel: (modelId: string) =>
    api.post(`/models/${modelId}/activate`),

  deleteModel: (modelId: string) =>
    api.delete(`/models/${modelId}`),
}
