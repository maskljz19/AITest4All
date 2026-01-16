/**
 * Export Panel Component
 * 导出面板组件 - 格式选择、内容选择、导出
 */
import React, { useState } from 'react'
import { Card, Radio, Checkbox, Button, Space, message, Divider } from 'antd'
import { DownloadOutlined } from '@ant-design/icons'
import type { CheckboxChangeEvent } from 'antd/es/checkbox'
import { exportApi } from '@/api/export'

interface ExportPanelProps {
  sessionId: string | null
  hasRequirement: boolean
  hasScenarios: boolean
  hasCases: boolean
  hasCode: boolean
  hasQualityReport: boolean
}

type ExportFormat = 'excel' | 'word' | 'json' | 'markdown' | 'html'
type ExportContent = 'requirement' | 'scenarios' | 'cases' | 'code' | 'quality_report'

const ExportPanel: React.FC<ExportPanelProps> = ({
  sessionId,
  hasRequirement,
  hasScenarios,
  hasCases,
  hasCode,
  hasQualityReport,
}) => {
  const [exportType, setExportType] = useState<'cases' | 'code'>('cases')
  const [caseFormat, setCaseFormat] = useState<ExportFormat>('excel')
  const [codeFormat, setCodeFormat] = useState<'zip' | 'single'>('zip')
  const [selectedContent, setSelectedContent] = useState<ExportContent[]>(['cases'])
  const [loading, setLoading] = useState(false)

  const handleContentChange = (content: ExportContent) => (e: CheckboxChangeEvent) => {
    if (e.target.checked) {
      setSelectedContent([...selectedContent, content])
    } else {
      setSelectedContent(selectedContent.filter((c) => c !== content))
    }
  }

  const handleExport = async () => {
    if (!sessionId) {
      message.error('会话ID不存在')
      return
    }

    if (selectedContent.length === 0) {
      message.error('请选择要导出的内容')
      return
    }

    setLoading(true)
    try {
      if (exportType === 'cases') {
        const response = await exportApi.exportCases({
          session_id: sessionId,
          format: caseFormat,
          include_requirement: selectedContent.includes('requirement'),
          include_scenarios: selectedContent.includes('scenarios'),
          include_cases: selectedContent.includes('cases'),
          include_quality_report: selectedContent.includes('quality_report'),
        })

        // Download file
        const blob = new Blob([response.data], {
          type: response.headers['content-type'],
        })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `test_cases_${Date.now()}.${caseFormat}`
        a.click()
        URL.revokeObjectURL(url)

        message.success('导出成功')
      } else {
        const response = await exportApi.exportCode({
          session_id: sessionId,
          format: codeFormat,
        })

        // Download file
        const blob = new Blob([response.data], {
          type: response.headers['content-type'],
        })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `test_code_${Date.now()}.${codeFormat === 'zip' ? 'zip' : 'txt'}`
        a.click()
        URL.revokeObjectURL(url)

        message.success('导出成功')
      }
    } catch (error: any) {
      message.error(error.response?.data?.message || '导出失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card title="导出配置" bordered={false}>
      <Space direction="vertical" style={{ width: '100%' }} size="large">
        {/* Export Type */}
        <div>
          <div style={{ marginBottom: 8, fontWeight: 500 }}>导出类型</div>
          <Radio.Group
            value={exportType}
            onChange={(e) => {
              setExportType(e.target.value)
              if (e.target.value === 'cases') {
                setSelectedContent(['cases'])
              } else {
                setSelectedContent(['code'])
              }
            }}
          >
            <Radio.Button value="cases" disabled={!hasCases}>
              测试用例
            </Radio.Button>
            <Radio.Button value="code" disabled={!hasCode}>
              测试代码
            </Radio.Button>
          </Radio.Group>
        </div>

        {exportType === 'cases' && (
          <>
            {/* Case Format */}
            <div>
              <div style={{ marginBottom: 8, fontWeight: 500 }}>导出格式</div>
              <Radio.Group value={caseFormat} onChange={(e) => setCaseFormat(e.target.value)}>
                <Radio.Button value="excel">Excel</Radio.Button>
                <Radio.Button value="word">Word</Radio.Button>
                <Radio.Button value="json">JSON</Radio.Button>
                <Radio.Button value="markdown">Markdown</Radio.Button>
                <Radio.Button value="html">HTML</Radio.Button>
              </Radio.Group>
            </div>

            {/* Content Selection */}
            <div>
              <div style={{ marginBottom: 8, fontWeight: 500 }}>导出内容</div>
              <Space direction="vertical">
                <Checkbox
                  checked={selectedContent.includes('requirement')}
                  onChange={handleContentChange('requirement')}
                  disabled={!hasRequirement}
                >
                  需求分析
                </Checkbox>
                <Checkbox
                  checked={selectedContent.includes('scenarios')}
                  onChange={handleContentChange('scenarios')}
                  disabled={!hasScenarios}
                >
                  测试场景
                </Checkbox>
                <Checkbox
                  checked={selectedContent.includes('cases')}
                  onChange={handleContentChange('cases')}
                  disabled={!hasCases}
                >
                  测试用例
                </Checkbox>
                <Checkbox
                  checked={selectedContent.includes('quality_report')}
                  onChange={handleContentChange('quality_report')}
                  disabled={!hasQualityReport}
                >
                  质量报告
                </Checkbox>
              </Space>
            </div>
          </>
        )}

        {exportType === 'code' && (
          <div>
            <div style={{ marginBottom: 8, fontWeight: 500 }}>导出格式</div>
            <Radio.Group value={codeFormat} onChange={(e) => setCodeFormat(e.target.value)}>
              <Radio.Button value="zip">ZIP压缩包（推荐）</Radio.Button>
              <Radio.Button value="single">单文件</Radio.Button>
            </Radio.Group>
            <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
              {codeFormat === 'zip'
                ? '将所有代码文件打包为ZIP压缩包，保持目录结构'
                : '将所有代码合并为一个文本文件'}
            </div>
          </div>
        )}

        <Divider />

        {/* Export Button */}
        <Button
          type="primary"
          size="large"
          icon={<DownloadOutlined />}
          onClick={handleExport}
          loading={loading}
          disabled={!sessionId || selectedContent.length === 0}
        >
          导出
        </Button>
      </Space>
    </Card>
  )
}

export default ExportPanel
