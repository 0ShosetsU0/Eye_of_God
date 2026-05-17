// frontend/src/pages/ProjectDetail.tsx
import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'

export default function ProjectDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [project, setProject] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchProject()
  }, [id])

  const fetchProject = async () => {
    try {
      const response = await api.get(`/api/v1/projects/${id}`)
      setProject(response.data)
    } catch (error) {
      console.error('Error fetching project:', error)
      toast.error('Ошибка загрузки проекта')
    } finally {
      setLoading(false)
    }
  }

  const handleUploadDataset = () => {
    navigate(`/projects/${id}/dataset`)
  }

  const handleStartTraining = () => {
    navigate(`/projects/${id}/training`)
  }

  const handleStartInspection = () => {
    navigate(`/projects/${id}/inspection`)
  }

  if (loading) {
    return <div className="p-6 text-center">Загрузка...</div>
  }

  if (!project) {
    return <div className="p-6 text-center text-red-500">Проект не найден</div>
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{project.name}</h1>
          <p className="text-gray-600 mt-1">{project.description || 'Нет описания'}</p>
        </div>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 text-gray-600 hover:text-gray-800"
        >
          ← Назад
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Датасет */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-2">Датасет</h2>
          <p className="text-3xl font-bold text-blue-600">
            {project.datasets_count || 0}
          </p>
          <p className="text-gray-500 text-sm mb-4">загруженных изображений</p>
          <button
            onClick={handleUploadDataset}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Загрузить датасет
          </button>
        </div>

        {/* Модели */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-2">Модели</h2>
          <p className="text-3xl font-bold text-green-600">
            {project.models_count || 0}
          </p>
          <p className="text-gray-500 text-sm mb-4">обученных моделей</p>
          <button
            onClick={handleStartTraining}
            className="w-full px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            Обучить модель
          </button>
        </div>

        {/* Инспекции */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-2">Инспекции</h2>
          <p className="text-3xl font-bold text-purple-600">
            {project.inspections_count || 0}
          </p>
          <p className="text-gray-500 text-sm mb-4">проверок</p>
          <button
            onClick={handleStartInspection}
            className="w-full px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Инспекция
          </button>
        </div>
      </div>
    </div>
  )
}