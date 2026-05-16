// frontend/src/services/newBackendAdapter.ts
import api from './api';

// Типы данных (адаптируйте под ваш бэкенд)
export interface User {
  id: string;
  email: string;
  name?: string;
  role?: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  createdAt?: string;
}

export interface DefectImage {
  id: string;
  url: string;
  defects?: any[];
}

// API вызовы (адаптируйте под эндпоинты вашего бэкенда)
export const newBackendApi = {
  // Авторизация
  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  register: (userData: any) =>
    api.post('/auth/register', userData),

  // Проекты
  getProjects: () =>
    api.get('/projects'),

  createProject: (data: any) =>
    api.post('/projects', data),

  getProject: (id: string) =>
    api.get(`/projects/${id}`),

  // Для работы с изображениями (адаптируйте под ваши эндпоинты)
  uploadImage: (file: File) => {
    const formData = new FormData();
    formData.append('image', file);
    return api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  getImages: () =>
    api.get('/images'),

  // Для ML (если есть в бэкенде)
  detectDefects: (imageId: string) =>
    api.post(`/detect/${imageId}`),
};