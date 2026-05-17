// frontend/src/pages/AnnotationPage.tsx
import { useParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { AnnotationTool } from '../components/Annotation/AnnotationTool'
import api from '../services/api'
import toast from 'react-hot-toast'

export default function AnnotationPage() {
  const { id, imageId } = useParams()
  const navigate = useNavigate()
  const [imageUrl, setImageUrl] = useState<string>('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadImage()
  }, [imageId])

  const loadImage = async () => {
    try {
      const response = await api.get(`/api/v1/datasets/images/${imageId}`)
      setImageUrl(response.data.url)
    } catch (error) {
      toast.error('Ошибка загрузки изображения')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveAnnotations = async (annotations: any[]) => {
    try {
      await api.post(`/api/v1/annotations/${imageId}`, { annotations })
      toast.success('Аннотации сохранены')
      navigate(`/projects/${id}/dataset`)
    } catch (error) {
      toast.error('Ошибка сохранения')
    }
  }

  if (loading) return <div className="p-6 text-center">Загрузка...</div>

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Разметка изображения</h1>
      <AnnotationTool
        imageUrl={imageUrl}
        onSave={handleSaveAnnotations}
      />
    </div>
  )
}