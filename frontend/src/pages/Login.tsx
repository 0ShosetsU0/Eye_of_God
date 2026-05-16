// frontend/src/pages/Login.tsx
import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import api from '../services/api'
import toast from 'react-hot-toast'

const Login: React.FC = () => {
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await api.post('/api/v1/auth/login', {
        email: email,
        password: password
      })

      const { access_token, refresh_token } = response.data

      // Сохраняем токены
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      // Создаем объект пользователя
      const user = {
        id: access_token.split('_')[1] || '1',
        email: email,
        username: email.split('@')[0]
      }

      setAuth(user, access_token, refresh_token)
      toast.success('Вход выполнен успешно')
      navigate('/')
    } catch (error: any) {
      console.error('Login error:', error)

      // Обрабатываем ошибку в правильном формате
      let errorMessage = 'Ошибка входа'

      if (error.response?.data) {
        const data = error.response.data
        if (typeof data === 'string') {
          errorMessage = data
        } else if (data.detail) {
          if (Array.isArray(data.detail)) {
            errorMessage = data.detail.map((d: any) => d.msg || d.message).join(', ')
          } else if (typeof data.detail === 'string') {
            errorMessage = data.detail
          } else {
            errorMessage = JSON.stringify(data.detail)
          }
        } else if (data.message) {
          errorMessage = data.message
        }
      }

      toast.error(errorMessage)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-8">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <div className="bg-blue-100 p-3 rounded-full text-2xl">🔍</div>
          </div>
          <h1 className="text-2xl font-bold text-gray-900">DefectVision</h1>
          <p className="text-gray-600 mt-2">Войдите в свою учетную запись</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="your@email.com"
              required
              autoFocus
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Пароль
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
          >
            {isLoading ? 'Вход...' : 'Войти'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Нет аккаунта?{' '}
            <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium">
              Зарегистрироваться
            </Link>
          </p>
        </div>

        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 text-center">
            Тестовый доступ:<br />
            Email: test@test.com<br />
            Пароль: 123456
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login