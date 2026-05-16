// frontend/src/services/projects.ts
/*import api from './api'
import { Project } from '../types'

export const projectsApi = {
  list: () => api.get<Project[]>('/projects'),
  get: (id: string) => api.get<Project>(`/projects/${id}`),
  create: (data: { name: string; description?: string }) =>
    api.post<Project>('/projects', data),
  update: (id: string, data: Partial<Project>) =>
    api.put<Project>(`/projects/${id}`, data),
  delete: (id: string) => api.delete(`/projects/${id}`),
}*/
// frontend/src/services/projects.ts (временная версия)
import { newBackendApi } from './newBackendAdapter';

export const projectsApi = {
  list: () => newBackendApi.getProjects(),
  get: (id: string) => newBackendApi.getProject(id),
  create: (data: any) => newBackendApi.createProject(data),
  update: (id: string, data: any) =>
    api.put(`/projects/${id}`, data),
  delete: (id: string) =>
    api.delete(`/projects/${id}`),
};