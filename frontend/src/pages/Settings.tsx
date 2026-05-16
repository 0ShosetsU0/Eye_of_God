// frontend/src/pages/Settings.tsx
import React, { useState } from 'react'
import { useAuthStore } from '../store/authStore'
import { User, Mail, Shield, Save } from 'lucide-react'
import api from '../services/api'
import toast from 'react-hot-toast'

const Settings: React.FC = () => {
  const { user, setAuth } = useAuthStore()
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [isLoading, setIsLoading] = useState(false)
  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const response = await api.put('/users/me', { full_name: fullName || null })
      if (user) {
        setAuth({ ...user, full_name: fullName },
                useAuthStore.getState().accessToken!,
                useAuthStore.getState().refreshToken!)
      }
      toast.success('Профиль обновлен')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка обновления')
    } finally {
      setIsLoading(false)
    }
  }

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()

    if (newPassword !== confirmPassword) {
      toast.error('Новые пароли не совпадают')
      return
    }

    if (newPassword.length < 6) {
      toast.error('Новый пароль должен содержать минимум 6 символов')
      return
    }

    setIsLoading(true)

    try {
      // Здесь будет API для смены пароля
      await api.post('/auth/change-password', {
        old_password: oldPassword,
        new_password: newPassword
      })

      toast.success('Пароль изменен')
      setOldPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка смены пароля')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Настройки</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Профиль */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <User className="h-5 w-5 text-blue-600" />
            <h2 className="text-lg font-semibold">Профиль</h2>
          </div>

          <form onSubmit={handleUpdateProfile} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="email"
                  value={user?.email || ''}
                  disabled
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Email нельзя изменить</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Имя пользователя
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  value={user?.username || ''}
                  disabled
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Полное имя
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ваше полное имя"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            >
              <Save className="h-4 w-4" />
              {isLoading ? 'Сохранение...' : 'Сохранить'}
            </button>
          </form>
        </div>

        {/* Смена пароля */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="h-5 w-5 text-blue-600" />
            <h2 className="text-lg font-semibold">Смена пароля</h2>
          </div>

          <form onSubmit={handleChangePassword} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Текущий пароль
              </label>
              <input
                type="password"
                value={oldPassword}
                onChange={(e) => setOldPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Новый пароль
              </label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
                minLength={6}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Подтверждение нового пароля
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
            >
              <Save className="h-4 w-4" />
              {isLoading ? 'Смена...' : 'Сменить пароль'}
            </button>
          </form>
        </div>
      </div>

      {/* Информация о системе */}
      <div className="mt-6 bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-2">О системе</h3>
        <p className="text-gray-600 text-sm">
          DefectVision - система автоматического обнаружения дефектов с использованием компьютерного зрения.
        </p>
        <p className="text-gray-500 text-xs mt-4">
          Версия 1.0.0
        </p>
      </div>
    </div>
  )
}

export default Settings