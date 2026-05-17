// frontend/src/components/Projects/ProjectCard.tsx
import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FolderOpen, Calendar, Activity, Trash2, Edit, MoreVertical } from 'lucide-react'
import { Project } from '../../types'
import api from '../../services/api'
import toast from 'react-hot-toast'
import { useQueryClient } from '@tanstack/react-query'

interface ProjectCardProps {
  project: Project
}

const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showMenu, setShowMenu] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800'
      case 'training': return 'bg-yellow-100 text-yellow-800'
      case 'archived': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Активен'
      case 'training': return 'Обучение'
      case 'archived': return 'Архив'
      default: return status
    }
  }

  const handleDelete = async () => {
    if (!confirm(`Удалить проект "${project.name}"? Это действие нельзя отменить.`)) {
      return
    }

    setIsDeleting(true)
    try {
      await api.delete(`/api/v1/projects/${project.id}`)
      toast.success('Проект удален')
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Ошибка удаления проекта'
      toast.error(message)
    } finally {
      setIsDeleting(false)
      setShowMenu(false)
    }
  }

  const handleEdit = () => {
    navigate(`/projects/${project.id}/edit`)
  }

  return (
    <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 relative">
      {/* Меню с тремя точками */}
      <div className="absolute top-4 right-4">
        <button
          onClick={() => setShowMenu(!showMenu)}
          className="p-1 rounded-full hover:bg-gray-100 transition-colors"
        >
          <MoreVertical className="h-5 w-5 text-gray-500" />
        </button>

        {showMenu && (
          <>
            <div className="fixed inset-0" onClick={() => setShowMenu(false)} />
            <div className="absolute right-0 mt-2 w-36 bg-white rounded-md shadow-lg z-10 border">
              <button
                onClick={handleEdit}
                className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
              >
                <Edit className="h-4 w-4" />
                Редактировать
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
              >
                <Trash2 className="h-4 w-4" />
                {isDeleting ? 'Удаление...' : 'Удалить'}
              </button>
            </div>
          </>
        )}
      </div>

      <Link to={`/projects/${project.id}`}>
        <div className="flex justify-between items-start mb-4">
          <FolderOpen className="h-10 w-10 text-blue-500" />
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
            {getStatusText(project.status)}
          </span>
        </div>

        <h3 className="text-lg font-semibold text-gray-900 mb-2">{project.name}</h3>
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
          {project.description || 'Нет описания'}
        </p>

        <div className="flex items-center justify-between text-sm text-gray-500 border-t pt-4">
          <div className="flex items-center">
            <Calendar className="h-4 w-4 mr-1" />
            {new Date(project.created_at).toLocaleDateString('ru-RU')}
          </div>
          <div className="flex items-center">
            <Activity className="h-4 w-4 mr-1" />
            {project.dataset_stats?.total_images || 0} изображений
          </div>
        </div>
      </Link>
    </div>
  )
}

export default ProjectCard