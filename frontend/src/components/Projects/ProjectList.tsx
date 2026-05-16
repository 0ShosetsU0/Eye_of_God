// frontend/src/components/Projects/ProjectList.tsx
import React from 'react'
import ProjectCard from './ProjectCard'
import { Project } from '../../types'

interface ProjectListProps {
  projects: Project[]
  isLoading?: boolean
}

const ProjectList: React.FC<ProjectListProps> = ({ projects, isLoading }) => {
  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="mt-2 text-gray-500">Загрузка проектов...</p>
      </div>
    )
  }

  if (projects.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">У вас пока нет проектов</p>
        <p className="text-sm text-gray-400 mt-1">Создайте первый проект, чтобы начать работу</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {projects.map((project) => (
        <ProjectCard key={project.id} project={project} />
      ))}
    </div>
  )
}

export default ProjectList