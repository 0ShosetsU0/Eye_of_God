import { useParams } from 'react-router-dom'
import { useState } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'

export default function DatasetManager() {
  const { id } = useParams()
  const [files, setFiles] = useState<FileList | null>(null)
  const [uploading, setUploading] = useState(false)

  const handleUpload = async () => {
    if (!files || files.length === 0) {
      toast.error('Выберите файлы для загрузки')
      return
    }

    setUploading(true)
    const formData = new FormData()
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i])
    }
    formData.append('project_id', id!)

    try {
      await api.post('/api/v1/datasets/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      toast.success('Файлы загружены')
    } catch (error) {
      toast.error('Ошибка загрузки')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Управление датасетом</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <input
          type="file"
          multiple
          onChange={(e) => setFiles(e.target.files)}
          className="mb-4"
          accept="image/*"
        />
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
        >
          {uploading ? 'Загрузка...' : 'Загрузить'}
        </button>
      </div>
    </div>
  )
}