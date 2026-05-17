// frontend/src/hooks/useWebSocket.ts
import { useEffect, useState, useRef } from 'react'
import { useAuthStore } from '../store/authStore'

export const useWebSocket = (projectId?: string) => {
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState<any[]>([])
  const wsRef = useRef<WebSocket | null>(null)
  const { accessToken } = useAuthStore()

  useEffect(() => {
    if (!accessToken || !projectId) return

    const ws = new WebSocket(`ws://localhost:8000/ws/${projectId}?token=${accessToken}`)
    wsRef.current = ws

    ws.onopen = () => {
      setIsConnected(true)
      console.log('WebSocket connected')
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setMessages(prev => [...prev, data])

      if (data.type === 'training_progress') {
        console.log(`Training progress: ${data.progress}%`)
      }
    }

    ws.onclose = () => {
      setIsConnected(false)
      console.log('WebSocket disconnected')
    }

    return () => {
      ws.close()
    }
  }, [accessToken, projectId])

  const send = (data: any) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify(data))
    }
  }

  return { isConnected, messages, send }
}