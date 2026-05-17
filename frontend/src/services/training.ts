// frontend/src/services/training.ts
import api from './api'
import { TrainingTask, TrainingConfig } from '../types'

export const trainingApi = {
  start: (projectId: string, config: TrainingConfig) =>
    api.post<{ task_id: string }>('/api/v1/training/start', {  // Добавлен /api/v1
      project_id: projectId,
      config,
    }),

  getStatus: (taskId: string) =>
    api.get<TrainingTask>(`/api/v1/training/status/${taskId}`),  // Добавлен /api/v1

  cancel: (taskId: string) =>
    api.post(`/api/v1/training/cancel/${taskId}`),  // Добавлен /api/v1

  getModels: (projectId: string) =>
    api.get('/api/v1/models', { params: { project_id: projectId } }),  // Добавлен /api/v1

  activateModel: (modelId: string) =>
    api.post(`/api/v1/models/${modelId}/activate`),  // Добавлен /api/v1

  deleteModel: (modelId: string) =>
    api.delete(`/api/v1/models/${modelId}`),  // Добавлен /api/v1
}