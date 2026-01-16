/**
 * Streaming Output Component
 * 流式输出展示组件 - WebSocket连接、实时更新、加载动画、中断
 */
import React, { useEffect, useState, useRef } from 'react'
import { Card, Button, Progress, Alert, Typography } from 'antd'
import { LoadingOutlined, StopOutlined, CheckCircleOutlined } from '@ant-design/icons'
import { WebSocketClient, StreamMessage } from '@/utils/websocket'

const { Text } = Typography

interface StreamingOutputProps {
  sessionId: string
  agentType: string
  onComplete?: (result: any) => void
  onError?: (error: string) => void
}

const StreamingOutput: React.FC<StreamingOutputProps> = ({
  sessionId,
  agentType,
  onComplete,
  onError,
}) => {
  const [content, setContent] = useState<string>('')
  const [status, setStatus] = useState<'connecting' | 'streaming' | 'done' | 'error'>('connecting')
  const [progress, setProgress] = useState<number>(0)
  const [currentStep, setCurrentStep] = useState<string>('')
  const [errorMessage, setErrorMessage] = useState<string>('')
  const wsRef = useRef<WebSocketClient | null>(null)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Initialize WebSocket connection
    const ws = new WebSocketClient(`/ws/generate?session_id=${sessionId}&agent=${agentType}`, {
      onMessage: handleMessage,
      onError: handleError,
      onClose: handleClose,
      onOpen: handleOpen,
    })

    ws.connect()
    wsRef.current = ws

    return () => {
      ws.close()
    }
  }, [sessionId, agentType])

  useEffect(() => {
    // Auto scroll to bottom when content updates
    if (contentRef.current) {
      contentRef.current.scrollTop = contentRef.current.scrollHeight
    }
  }, [content])

  const handleOpen = () => {
    setStatus('streaming')
  }

  const handleMessage = (message: StreamMessage) => {
    if (message.type === 'chunk') {
      setContent((prev) => prev + (message.content || ''))
      if (message.metadata) {
        setCurrentStep(message.metadata.step || '')
        if (message.metadata.progress !== undefined) {
          setProgress(message.metadata.progress)
        }
      }
    } else if (message.type === 'done') {
      setStatus('done')
      setProgress(100)
      if (onComplete) {
        try {
          const result = JSON.parse(content + (message.content || ''))
          onComplete(result)
        } catch (error) {
          // If not JSON, pass as string
          onComplete(content + (message.content || ''))
        }
      }
    } else if (message.type === 'error') {
      setStatus('error')
      const error = message.error || '未知错误'
      setErrorMessage(error)
      if (onError) {
        onError(error)
      }
    }
  }

  const handleError = (_error: Event) => {
    setStatus('error')
    setErrorMessage('WebSocket连接错误')
    if (onError) {
      onError('WebSocket连接错误')
    }
  }

  const handleClose = () => {
    if (status === 'streaming') {
      setStatus('error')
      setErrorMessage('连接已断开')
    }
  }

  const handleStop = () => {
    if (wsRef.current) {
      wsRef.current.close()
      setStatus('error')
      setErrorMessage('用户中断')
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'connecting':
        return <LoadingOutlined spin />
      case 'streaming':
        return <LoadingOutlined spin />
      case 'done':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />
      case 'error':
        return null
      default:
        return null
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'connecting':
        return '正在连接...'
      case 'streaming':
        return currentStep || '正在生成...'
      case 'done':
        return '生成完成'
      case 'error':
        return '生成失败'
      default:
        return ''
    }
  }

  return (
    <Card
      title={
        <span>
          {getStatusIcon()} <span style={{ marginLeft: 8 }}>{getStatusText()}</span>
        </span>
      }
      bordered={false}
      extra={
        status === 'streaming' && (
          <Button danger icon={<StopOutlined />} onClick={handleStop}>
            中断
          </Button>
        )
      }
    >
      {status === 'error' && (
        <Alert
          message="生成失败"
          description={errorMessage}
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {(status === 'streaming' || status === 'connecting') && (
        <Progress
          percent={progress}
          status="active"
          strokeColor={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
          style={{ marginBottom: 16 }}
        />
      )}

      {status === 'done' && (
        <Alert
          message="生成完成"
          description="内容已成功生成"
          type="success"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      <div
        ref={contentRef}
        style={{
          maxHeight: 400,
          overflow: 'auto',
          padding: 16,
          backgroundColor: '#f5f5f5',
          borderRadius: 4,
          fontFamily: 'monospace',
          fontSize: 12,
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}
      >
        {content || (
          <Text type="secondary">
            {status === 'connecting' ? '等待连接...' : '等待内容...'}
          </Text>
        )}
      </div>
    </Card>
  )
}

export default StreamingOutput
