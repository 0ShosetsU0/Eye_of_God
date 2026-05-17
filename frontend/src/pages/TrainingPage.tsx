import { useParams } from 'react-router-dom'
import { useState } from 'react'
import api from '../services/api'
import toast from 'react-hot-toast'

export default function TrainingPage() {
  const { id } = useParams()
  const [epochs, setEpochs] = useState(100)
  const [training, setTraining] = useState(false)

  const startTraining = async () => {
    setTraining(true)
    try {
      await api.post(`/api/v1/training/start`, {
        project_id: id,
        config: { epochs, model_type: 'yolo' }
      })
      toast.success('Обучение запущено')
    } catch (error) {
      toast.error('Ошибка запуска обучения')
    } finally {
      setTraining(false)
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Обучение модели</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">Количество эпох</label>
          <input
            type="number"
            value={epochs}
            onChange={(e) => setEpochs(parseInt(e.target.value))}
            className="border rounded px-3 py-2 w-32"
            min={1}
            max={1000}
          />
        </div>
        <button
          onClick={startTraining}
          disabled={training}
          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400"
        >
          {training ? 'Запуск...' : 'Начать обучение'}
        </button>
      </div>
    </div>
  )
}