// frontend/src/pages/Dashboard.tsx
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi } from '../services/projects'
import ProjectCard from '../components/Projects/ProjectCard'
import ProjectForm from '../components/Projects/ProjectForm'
import LoadingSpinner from '../components/Common/LoadingSpinner'
import toast from 'react-hot-toast'

export default function Dashboard() {
  const [showCreateModal, setShowCreateModal] = useState(false)
  const queryClient = useQueryClient()

  const { data: projects, isLoading, error } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.list().then(res => res.data),
  })

  const createMutation = useMutation({
    mutationFn: projectsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
      setShowCreateModal(false)
      toast.success('Проект создан')
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Ошибка создания проекта'
      toast.error(message)
    },
  })

  if (isLoading) return <LoadingSpinner />

  if (error) {
    return (
      <div className="p-6 text-center text-red-500">
        Ошибка загрузки проектов: {(error as any).message}
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Мои проекты</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Новый проект
        </button>
      </div>

      {projects?.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">У вас пока нет проектов</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            Создать первый проект
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects?.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}

      {showCreateModal && (
        <ProjectForm
          onSubmit={(data) => createMutation.mutate(data)}
          onClose={() => setShowCreateModal(false)}
          isLoading={createMutation.isPending}
        />
      )}
    </div>
  )
}