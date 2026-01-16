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

export interface WebSocketOptions {
  onMessage: (message: StreamMessage) => void
  onError?: (error: Event) => void
  onClose?: () => void
  onOpen?: () => void
  reconnect?: boolean
  reconnectInterval?: number
  maxReconnectAttempts?: number
}

export class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private options: WebSocketOptions
  private reconnectAttempts = 0
  private shouldReconnect = true
  private reconnectTimer: number | null = null

  constructor(endpoint: string, options: WebSocketOptions) {
    this.url = `${WS_BASE_URL}${endpoint}`
    this.options = {
      reconnect: true,
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
      ...options,
    }
  }

  connect(): void {
    try {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        if (this.options.onOpen) {
          this.options.onOpen()
        }
      }

      this.ws.onmessage = (event) => {
        try {
          const message: StreamMessage = JSON.parse(event.data)
          this.options.onMessage(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        if (this.options.onError) {
          this.options.onError(error)
        }
      }

      this.ws.onclose = () => {
        console.log('WebSocket closed')
        if (this.options.onClose) {
          this.options.onClose()
        }

        // Attempt to reconnect if enabled
        if (
          this.shouldReconnect &&
          this.options.reconnect &&
          this.reconnectAttempts < (this.options.maxReconnectAttempts || 5)
        ) {
          this.reconnectAttempts++
          console.log(
            `Attempting to reconnect (${this.reconnectAttempts}/${this.options.maxReconnectAttempts})...`
          )
          this.reconnectTimer = window.setTimeout(() => {
            this.connect()
          }, this.options.reconnectInterval || 3000)
        }
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
    }
  }

  send(data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  close(): void {
    this.shouldReconnect = false
    if (this.reconnectTimer) {
      window.clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

export default WebSocketClient
