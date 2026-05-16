// frontend/src/pages/InspectionPage.tsx
import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Upload, Camera, FileImage, CheckCircle, XCircle } from 'lucide-react'
import { inspectionApi } from '../services/inspection'
import ResultViewer from '../components/Inspection/ResultViewer'
import ImageUploader from '../components/Inspection/ImageUploader'
import toast from 'react-hot-toast'
import { InspectionResult } from '../types'

export default function InspectionPage() {
  const { id: projectId } = useParams()
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [result, setResult] = useState<InspectionResult | null>(null)
  const [threshold, setThreshold] = useState(0.5)

  const inspectMutation = useMutation({
    mutationFn: (data: { image: File; threshold: number }) =>
      inspectionApi.inspect(projectId!, data.image, data.threshold),
    onSuccess: (res) => {
      setResult(res.data)
      toast.success('Анализ завершен')
    },
    onError: () => toast.error('Ошибка при анализе'),
  })

  const handleImageSelect = (file: File) => {
    setSelectedImage(file)
    setResult(null)
  }

  const handleInspect = () => {
    if (selectedImage) {
      inspectMutation.mutate({ image: selectedImage, threshold })
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Инспекция</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Левая колонка - загрузка и настройки */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Загрузка изображения</h2>
            <ImageUploader onImageSelect={handleImageSelect} />

            {selectedImage && (
              <div className="mt-4">
                <img
                  src={URL.createObjectURL(selectedImage)}
                  alt="Preview"
                  className="max-h-64 rounded-lg border"
                />
                <p className="text-sm text-gray-500 mt-2">
                  {selectedImage.name} ({(selectedImage.size / 1024).toFixed(0)} KB)
                </p>
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Настройки</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Порог уверенности: {threshold}
              </label>
              <input
                type="range"
                min={0}
                max={1}
                step={0.05}
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            <button
              onClick={handleInspect}
              disabled={!selectedImage || inspectMutation.isPending}
              className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
            >
              {inspectMutation.isPending ? 'Анализ...' : 'Начать анализ'}
            </button>
          </div>
        </div>

        {/* Правая колонка - результаты */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Результаты</h2>
          {result ? (
            <ResultViewer
              imageUrl={result.image_url}
              resultUrl={result.result_url}
              defects={result.defects}
              processingTime={result.processing_time_ms}
              onFeedback={(isCorrect, comment) => {
                inspectionApi.sendFeedback(result.id, isCorrect, undefined, comment)
                toast.success('Спасибо за обратную связь!')
              }}
            />
          ) : (
            <div className="text-center py-12 text-gray-400">
              <Camera size={48} className="mx-auto mb-4" />
              <p>Загрузите изображение и начните анализ</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}