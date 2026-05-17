import { useParams } from 'react-router-dom'
import { useState } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'

export default function InspectionPage() {
  const { id } = useParams()
  const [file, setFile] = useState<File | null>(null)
  const [result, setResult] = useState<any>(null)
  const [inspecting, setInspecting] = useState(false)

  const handleInspect = async () => {
    if (!file) {
      toast.error('Выберите изображение')
      return
    }

    setInspecting(true)
    const formData = new FormData()
    formData.append('image', file)
    formData.append('project_id', id!)

    try {
      const response = await api.post('/api/v1/inspection/single', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setResult(response.data)
      toast.success('Анализ завершен')
    } catch (error) {
      toast.error('Ошибка анализа')
    } finally {
      setInspecting(false)
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Инспекция</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="mb-4"
          accept="image/*"
        />
        <button
          onClick={handleInspect}
          disabled={inspecting || !file}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400"
        >
          {inspecting ? 'Анализ...' : 'Начать анализ'}
        </button>

        {result && (
          <div className="mt-6">
            <h3 className="font-semibold mb-2">Результаты:</h3>
            <pre className="bg-gray-100 p-4 rounded overflow-auto">
              {JSON.stringify(result.defects, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}