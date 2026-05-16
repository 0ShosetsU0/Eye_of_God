// frontend/src/components/Common/LoadingSpinner.tsx
import React from 'react'

const LoadingSpinner: React.FC = () => {
  return (
    <div className="flex justify-center items-center h-64">
      <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
    </div>
  )
}

export default LoadingSpinner