// frontend/src/components/Projects/ProjectCard.tsx
import React from 'react'
import { Link } from 'react-router-dom'
import { Project } from '../../types'

interface ProjectCardProps {
  project: Project
}

const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
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

  return (
    <Link to={`/projects/${project.id}`}>
      <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 cursor-pointer">
        <div className="flex justify-between items-start mb-4">
          <div className="text-3xl">📁</div>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
            {getStatusText(project.status)}
          </span>
        </div>

        <h3 className="text-lg font-semibold text-gray-900 mb-2">{project.name}</h3>
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
          {project.description || 'Нет описания'}
        </p>

        <div className="flex items-center justify-between text-sm text-gray-500 border-t pt-4">
          <div>
            📅 {new Date(project.created_at).toLocaleDateString('ru-RU')}
          </div>
          <div>
            🖼️ {project.dataset_stats?.total_images || 0} изображений
          </div>
        </div>
      </div>
    </Link>
  )
}

export default ProjectCard