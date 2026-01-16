/**
 * Requirement Input Component
 * 需求输入组件 - 支持文件上传、URL输入、文本输入
 */
import React, { useState } from 'react'
import { Card, Form, Input, Upload, Radio, Select, Button, message, Space, Tabs } from 'antd'
import { UploadOutlined, LinkOutlined, FileTextOutlined } from '@ant-design/icons'
import type { UploadFile } from 'antd/es/upload/interface'
import { TestType } from '@/types'

const { TextArea } = Input
const { TabPane } = Tabs

export interface RequirementInputData {
  inputType: 'file' | 'url' | 'text'
  file?: File
  url?: string
  text?: string
  testType: TestType
  knowledgeBaseIds: number[]
}

interface RequirementInputProps {
  onSubmit: (data: RequirementInputData) => void
  loading?: boolean
  knowledgeBases?: Array<{ id: number; name: string; type: string }>
}

const RequirementInput: React.FC<RequirementInputProps> = ({
  onSubmit,
  loading = false,
  knowledgeBases = [],
}) => {
  const [form] = Form.useForm()
  const [inputType, setInputType] = useState<'file' | 'url' | 'text'>('text')
  const [fileList, setFileList] = useState<UploadFile[]>([])

  const handleSubmit = () => {
    form.validateFields().then((values) => {
      const data: RequirementInputData = {
        inputType,
        testType: values.testType,
        knowledgeBaseIds: values.knowledgeBaseIds || [],
      }

      if (inputType === 'file') {
        if (fileList.length === 0) {
          message.error('请上传需求文档')
          return
        }
        data.file = fileList[0].originFileObj as File
      } else if (inputType === 'url') {
        if (!values.url) {
          message.error('请输入URL')
          return
        }
        data.url = values.url
      } else {
        if (!values.text) {
          message.error('请输入需求文本')
          return
        }
        data.text = values.text
      }

      onSubmit(data)
    })
  }

  const handleFileChange = (info: any) => {
    let newFileList = [...info.fileList]
    // Only keep the last file
    newFileList = newFileList.slice(-1)
    setFileList(newFileList)
  }

  const beforeUpload = (file: File) => {
    const isValidType =
      file.type === 'application/pdf' ||
      file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
      file.type === 'text/markdown' ||
      file.type === 'text/plain' ||
      file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    if (!isValidType) {
      message.error('只支持 PDF、Word、Markdown、TXT、Excel 格式')
      return false
    }

    const isLt10M = file.size / 1024 / 1024 < 10
    if (!isLt10M) {
      message.error('文件大小不能超过 10MB')
      return false
    }

    return false // Prevent auto upload
  }

  return (
    <Card title="需求输入" bordered={false}>
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          testType: 'ui',
          knowledgeBaseIds: [],
        }}
      >
        <Form.Item label="输入方式">
          <Tabs activeKey={inputType} onChange={(key) => setInputType(key as any)}>
            <TabPane
              tab={
                <span>
                  <FileTextOutlined />
                  文本输入
                </span>
              }
              key="text"
            />
            <TabPane
              tab={
                <span>
                  <UploadOutlined />
                  文件上传
                </span>
              }
              key="file"
            />
            <TabPane
              tab={
                <span>
                  <LinkOutlined />
                  URL链接
                </span>
              }
              key="url"
            />
          </Tabs>
        </Form.Item>

        {inputType === 'text' && (
          <Form.Item
            name="text"
            label="需求文本"
            rules={[{ required: true, message: '请输入需求文本' }]}
          >
            <TextArea
              rows={10}
              placeholder="请输入需求文档内容，支持纯文本或Markdown格式"
              disabled={loading}
            />
          </Form.Item>
        )}

        {inputType === 'file' && (
          <Form.Item label="上传文件">
            <Upload
              fileList={fileList}
              onChange={handleFileChange}
              beforeUpload={beforeUpload}
              maxCount={1}
              accept=".pdf,.docx,.md,.txt,.xlsx"
              disabled={loading}
            >
              <Button icon={<UploadOutlined />} disabled={loading}>
                选择文件
              </Button>
            </Upload>
            <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
              支持格式: PDF、Word、Markdown、TXT、Excel，文件大小不超过 10MB
            </div>
          </Form.Item>
        )}

        {inputType === 'url' && (
          <Form.Item
            name="url"
            label="URL链接"
            rules={[
              { required: true, message: '请输入URL' },
              { type: 'url', message: '请输入有效的URL' },
            ]}
          >
            <Input
              prefix={<LinkOutlined />}
              placeholder="https://example.com/requirement.html"
              disabled={loading}
            />
          </Form.Item>
        )}

        <Form.Item
          name="testType"
          label="测试类型"
          rules={[{ required: true, message: '请选择测试类型' }]}
        >
          <Radio.Group disabled={loading}>
            <Radio.Button value="ui">UI测试</Radio.Button>
            <Radio.Button value="api">接口测试</Radio.Button>
            <Radio.Button value="unit">单元测试</Radio.Button>
          </Radio.Group>
        </Form.Item>

        <Form.Item name="knowledgeBaseIds" label="关联知识库（可选）">
          <Select
            mode="multiple"
            placeholder="选择要关联的知识库"
            disabled={loading}
            options={knowledgeBases.map((kb) => ({
              label: `${kb.name} (${kb.type})`,
              value: kb.id,
            }))}
            allowClear
          />
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" onClick={handleSubmit} loading={loading} size="large">
              开始分析
            </Button>
            <Button onClick={() => form.resetFields()} disabled={loading}>
              重置
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  )
}

export default RequirementInput
