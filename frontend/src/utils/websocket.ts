/**
 * WebSocket Client for Streaming
 */

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'

export interface StreamMessage {
  type: 'chunk' | 'done' | 'error'
  content?: string
  error?: string
  metadata?: {
    agent: string
    step: string
    progress?: number
  }
}

export class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string

  constructor(endpoint: string) {
    this.url = `${WS_BASE_URL}${endpoint}`
  }

  connect(
    onMessage: (message: StreamMessage) => void,
    onError?: (error: Event) => void,
    onClose?: () => void
  ): void {
    this.ws = new WebSocket(this.url)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
    }

    this.ws.onmessage = (event) => {
      try {
        const message: StreamMessage = JSON.parse(event.data)
        onMessage(message)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (onError) {
        onError(error)
      }
    }

    this.ws.onclose = () => {
      console.log('WebSocket closed')
      if (onClose) {
        onClose()
      }
    }
  }

  send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  close(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

export default WebSocketClient
