/**
 * Code Generation Component
 * 代码生成组件 - 技术栈配置、代码预览、文件树、编辑
 */
import React, { useState } from 'react'
import { Card, Row, Col, Radio, Input, Button, Tree, Space, message } from 'antd'
import { FolderOutlined, FileOutlined, DownloadOutlined } from '@ant-design/icons'
import Editor from '@monaco-editor/react'
import type { DataNode } from 'antd/es/tree'
import { CodeFiles } from '@/types'

const { TextArea } = Input

interface CodeGenerationProps {
  codeFiles: CodeFiles | null
  onGenerate: (useDefaultStack: boolean, techStack?: string) => void
  onUpdate: (files: CodeFiles) => void
  loading?: boolean
}

const CodeGeneration: React.FC<CodeGenerationProps> = ({
  codeFiles,
  onGenerate,
  onUpdate,
  loading = false,
}) => {
  const [useDefaultStack, setUseDefaultStack] = useState(true)
  const [customTechStack, setCustomTechStack] = useState('')
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const [editedContent, setEditedContent] = useState<string>('')

  // Build file tree from code files
  const buildFileTree = (files: Record<string, string>): DataNode[] => {
    const tree: DataNode[] = []
    const fileNames = Object.keys(files)

    fileNames.forEach((fileName) => {
      const parts = fileName.split('/')
      let currentLevel = tree

      parts.forEach((part, index) => {
        const isFile = index === parts.length - 1
        const existingNode = currentLevel.find((node) => node.title === part)

        if (existingNode) {
          if (!isFile && existingNode.children) {
            currentLevel = existingNode.children as DataNode[]
          }
        } else {
          const newNode: DataNode = {
            title: part,
            key: fileName,
            icon: isFile ? <FileOutlined /> : <FolderOutlined />,
            children: isFile ? undefined : [],
          }
          currentLevel.push(newNode)
          if (!isFile && newNode.children) {
            currentLevel = newNode.children as DataNode[]
          }
        }
      })
    })

    return tree
  }

  const handleGenerate = () => {
    if (!useDefaultStack && !customTechStack.trim()) {
      message.error('请输入自定义技术栈描述')
      return
    }
    onGenerate(useDefaultStack, useDefaultStack ? undefined : customTechStack)
  }

  const handleFileSelect = (selectedKeys: React.Key[]) => {
    if (selectedKeys.length > 0 && codeFiles) {
      const fileName = selectedKeys[0] as string
      if (codeFiles.files[fileName]) {
        setSelectedFile(fileName)
        setEditedContent(codeFiles.files[fileName])
      }
    }
  }

  const handleSaveEdit = () => {
    if (selectedFile && codeFiles) {
      const updatedFiles = {
        ...codeFiles.files,
        [selectedFile]: editedContent,
      }
      onUpdate({ files: updatedFiles })
      message.success('保存成功')
    }
  }

  const handleDownload = () => {
    if (!codeFiles) return

    // Create a simple download of all files as text
    const content = Object.entries(codeFiles.files)
      .map(([fileName, fileContent]) => {
        return `// File: ${fileName}\n${'='.repeat(80)}\n${fileContent}\n\n`
      })
      .join('\n')

    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'test_code.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  const getLanguage = (fileName: string): string => {
    const ext = fileName.split('.').pop()?.toLowerCase()
    const languageMap: Record<string, string> = {
      py: 'python',
      js: 'javascript',
      ts: 'typescript',
      java: 'java',
      json: 'json',
      yaml: 'yaml',
      yml: 'yaml',
      md: 'markdown',
      txt: 'plaintext',
    }
    return languageMap[ext || ''] || 'plaintext'
  }

  return (
    <Card title="代码生成" bordered={false}>
      {!codeFiles ? (
        <div>
          <Space direction="vertical" style={{ width: '100%' }} size="large">
            <div>
              <div style={{ marginBottom: 8, fontWeight: 500 }}>技术栈选择</div>
              <Radio.Group
                value={useDefaultStack}
                onChange={(e) => setUseDefaultStack(e.target.value)}
                disabled={loading}
              >
                <Space direction="vertical">
                  <Radio value={true}>
                    使用默认技术栈
                    <div style={{ marginLeft: 24, color: '#999', fontSize: 12 }}>
                      UI测试: Pytest + Selenium + Page Object Model
                      <br />
                      接口测试: Pytest + Requests
                      <br />
                      单元测试: Pytest + Mock
                    </div>
                  </Radio>
                  <Radio value={false}>自定义技术栈</Radio>
                </Space>
              </Radio.Group>
            </div>

            {!useDefaultStack && (
              <div>
                <div style={{ marginBottom: 8, fontWeight: 500 }}>技术栈描述</div>
                <TextArea
                  rows={4}
                  placeholder="请描述您希望使用的技术栈，例如：使用Java + TestNG + RestAssured进行接口测试"
                  value={customTechStack}
                  onChange={(e) => setCustomTechStack(e.target.value)}
                  disabled={loading}
                />
              </div>
            )}

            <Button type="primary" size="large" onClick={handleGenerate} loading={loading}>
              生成代码
            </Button>
          </Space>
        </div>
      ) : (
        <Row gutter={16}>
          <Col span={6}>
            <Card title="文件树" size="small" bodyStyle={{ padding: 8 }}>
              <Tree
                showIcon
                defaultExpandAll
                treeData={buildFileTree(codeFiles.files)}
                onSelect={handleFileSelect}
                selectedKeys={selectedFile ? [selectedFile] : []}
              />
            </Card>
          </Col>
          <Col span={18}>
            <Card
              title={selectedFile || '代码预览'}
              size="small"
              extra={
                <Space>
                  <Button onClick={handleSaveEdit} disabled={!selectedFile || loading}>
                    保存修改
                  </Button>
                  <Button icon={<DownloadOutlined />} onClick={handleDownload}>
                    下载全部
                  </Button>
                </Space>
              }
              bodyStyle={{ padding: 0 }}
            >
              {selectedFile ? (
                <Editor
                  height="600px"
                  language={getLanguage(selectedFile)}
                  value={editedContent}
                  onChange={(value) => setEditedContent(value || '')}
                  theme="vs-dark"
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: 'on',
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                  }}
                />
              ) : (
                <div
                  style={{
                    height: 600,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#999',
                  }}
                >
                  请从左侧选择文件查看
                </div>
              )}
            </Card>
          </Col>
        </Row>
      )}
    </Card>
  )
}

export default CodeGeneration
