// frontend/src/components/Common/ErrorAlert.tsx
import React from 'react'
import { AlertCircle, X } from 'lucide-react'

interface ErrorAlertProps {
  message: string
  onClose?: () => void
}

const ErrorAlert: React.FC<ErrorAlertProps> = ({ message, onClose }) => {
  if (!message) return null

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
      <div className="flex items-start">
        <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
        <div className="ml-3 flex-1">
          <p className="text-sm text-red-800">{message}</p>
        </div>
        {onClose && (
          <button onClick={onClose} className="text-red-500 hover:text-red-700">
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  )
}

export default ErrorAlert