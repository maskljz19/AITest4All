import React, { useState, useEffect } from 'react'
import {
  Card,
  Button,
  Table,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Upload,
  message,
  Tag,
  Popconfirm,
  Drawer,
  Typography,
  Tabs,
} from 'antd'
import {
  UploadOutlined,
  LinkOutlined,
  DeleteOutlined,
  EyeOutlined,
  SearchOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import type { UploadFile } from 'antd/es/upload/interface'
import { knowledgeBaseApi } from '../api/knowledgeBase'

const { Paragraph } = Typography
const { TabPane } = Tabs

interface KnowledgeBase {
  id: number
  name: string
  type: 'case' | 'defect' | 'rule' | 'api'
  storage_type: 'local' | 'url' | 'database'
  file_path?: string
  url?: string
  content?: string
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

const KnowledgeBasePage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [dataSource, setDataSource] = useState<KnowledgeBase[]>([])
  const [uploadModalVisible, setUploadModalVisible] = useState(false)
  const [urlModalVisible, setUrlModalVisible] = useState(false)
  const [previewDrawerVisible, setPreviewDrawerVisible] = useState(false)
  const [selectedKb, setSelectedKb] = useState<KnowledgeBase | null>(null)
  const [searchText, setSearchText] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  
  const [uploadForm] = Form.useForm()
  const [urlForm] = Form.useForm()
  const [fileList, setFileList] = useState<UploadFile[]>([])

  // 加载知识库列表
  const loadKnowledgeBases = async () => {
    setLoading(true)
    try {
      const response = await knowledgeBaseApi.getList()
      setDataSource(Array.isArray(response.data.data) ? response.data.data : [])
    } catch (error: any) {
      message.error(error.response?.data?.message || '加载知识库列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadKnowledgeBases()
  }, [])

  // 文件上传
  const handleUpload = async (values: any) => {
    if (fileList.length === 0) {
      message.error('请选择文件')
      return
    }

    setLoading(true)
    try {
      await knowledgeBaseApi.uploadDocument({
        file: fileList[0].originFileObj as File,
        name: values.name,
        type: values.type,
      })
      message.success('上传成功')
      setUploadModalVisible(false)
      uploadForm.resetFields()
      setFileList([])
      loadKnowledgeBases()
    } catch (error: any) {
      message.error(error.response?.data?.message || '上传失败')
    } finally {
      setLoading(false)
    }
  }

  // URL添加
  const handleAddUrl = async (values: any) => {
    setLoading(true)
    try {
      await knowledgeBaseApi.addUrl({
        url: values.url,
        name: values.name,
        type: values.type,
      })
      message.success('添加成功')
      setUrlModalVisible(false)
      urlForm.resetFields()
      loadKnowledgeBases()
    } catch (error: any) {
      message.error(error.response?.data?.message || '添加失败')
    } finally {
      setLoading(false)
    }
  }

  // 删除知识库
  const handleDelete = async (id: number) => {
    setLoading(true)
    try {
      await knowledgeBaseApi.deleteDocument(id)
      message.success('删除成功')
      loadKnowledgeBases()
    } catch (error: any) {
      message.error(error.response?.data?.message || '删除失败')
    } finally {
      setLoading(false)
    }
  }

  // 预览知识库
  const handlePreview = async (record: KnowledgeBase) => {
    setLoading(true)
    try {
      const response = await knowledgeBaseApi.getDetail(record.id)
      setSelectedKb(response.data.data)
      setPreviewDrawerVisible(true)
    } catch (error: any) {
      message.error(error.response?.data?.message || '加载详情失败')
    } finally {
      setLoading(false)
    }
  }

  // 搜索知识库
  const handleSearch = async () => {
    if (!searchText.trim()) {
      message.warning('请输入搜索关键词')
      return
    }

    setLoading(true)
    try {
      const response = await knowledgeBaseApi.search({
        query: searchText,
        type: filterType === 'all' ? undefined : filterType,
      })
      setDataSource(Array.isArray(response.data.data) ? response.data.data : [])
    } catch (error: any) {
      message.error(error.response?.data?.message || '搜索失败')
    } finally {
      setLoading(false)
    }
  }

  // 类型标签颜色
  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      case: 'blue',
      defect: 'red',
      rule: 'green',
      api: 'orange',
    }
    return colors[type] || 'default'
  }

  // 类型标签文本
  const getTypeText = (type: string) => {
    const texts: Record<string, string> = {
      case: '用例',
      defect: '缺陷',
      rule: '规则',
      api: '接口',
    }
    return texts[type] || type
  }

  // 表格列定义
  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 100,
      render: (type: string) => (
        <Tag color={getTypeColor(type)}>{getTypeText(type)}</Tag>
      ),
    },
    {
      title: '存储方式',
      dataIndex: 'storage_type',
      key: 'storage_type',
      width: 120,
      render: (storageType: string) => {
        const texts: Record<string, string> = {
          local: '本地文件',
          url: '外部链接',
          database: '数据库',
        }
        return texts[storageType] || storageType
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text: string) => new Date(text).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: KnowledgeBase) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handlePreview(record)}
          >
            预览
          </Button>
          <Popconfirm
            title="确定删除此知识库吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>知识库管理</h1>

      <Card>
        {/* 操作栏 */}
        <Space style={{ marginBottom: 16 }} wrap>
          <Button
            type="primary"
            icon={<UploadOutlined />}
            onClick={() => setUploadModalVisible(true)}
          >
            上传文档
          </Button>
          <Button
            icon={<LinkOutlined />}
            onClick={() => setUrlModalVisible(true)}
          >
            添加外链
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={loadKnowledgeBases}
          >
            刷新
          </Button>
        </Space>

        {/* 搜索和筛选 */}
        <Space style={{ marginBottom: 16, width: '100%' }} wrap>
          <Select
            style={{ width: 120 }}
            value={filterType}
            onChange={setFilterType}
            options={[
              { label: '全部类型', value: 'all' },
              { label: '用例', value: 'case' },
              { label: '缺陷', value: 'defect' },
              { label: '规则', value: 'rule' },
              { label: '接口', value: 'api' },
            ]}
          />
          <Input.Search
            placeholder="搜索知识库内容"
            style={{ width: 300 }}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onSearch={handleSearch}
            enterButton={<SearchOutlined />}
          />
        </Space>

        {/* 表格 */}
        <Table
          columns={columns}
          dataSource={dataSource}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>

      {/* 上传文档模态框 */}
      <Modal
        title="上传文档"
        open={uploadModalVisible}
        onCancel={() => {
          setUploadModalVisible(false)
          uploadForm.resetFields()
          setFileList([])
        }}
        onOk={() => uploadForm.submit()}
        confirmLoading={loading}
      >
        <Form form={uploadForm} layout="vertical" onFinish={handleUpload}>
          <Form.Item
            name="name"
            label="文档名称"
            rules={[{ required: true, message: '请输入文档名称' }]}
          >
            <Input placeholder="请输入文档名称" />
          </Form.Item>

          <Form.Item
            name="type"
            label="文档类型"
            rules={[{ required: true, message: '请选择文档类型' }]}
          >
            <Select
              placeholder="请选择文档类型"
              options={[
                { label: '用例', value: 'case' },
                { label: '缺陷', value: 'defect' },
                { label: '规则', value: 'rule' },
                { label: '接口', value: 'api' },
              ]}
            />
          </Form.Item>

          <Form.Item label="选择文件" required>
            <Upload
              fileList={fileList}
              beforeUpload={(file) => {
                // 支持的文件扩展名
                const allowedExtensions = ['.doc', '.docx', '.pdf', '.md', '.txt', '.xls', '.xlsx']
                const fileName = file.name.toLowerCase()
                const isValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext))

                // 支持的MIME类型
                const allowedMimeTypes = [
                  'application/pdf',
                  'application/msword', // .doc
                  'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
                  'text/markdown',
                  'text/plain',
                  'application/vnd.ms-excel', // .xls
                  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
                ]
                const isValidMimeType = allowedMimeTypes.includes(file.type)

                // 检查文件扩展名或MIME类型
                if (!isValidExtension && !isValidMimeType) {
                  message.error('只支持 PDF、Word (.doc/.docx)、Markdown、TXT、Excel (.xls/.xlsx) 格式')
                  return false
                }

                const isLt10M = file.size / 1024 / 1024 < 10
                if (!isLt10M) {
                  message.error('文件大小不能超过10MB')
                  return false
                }
                setFileList([file])
                return false
              }}
              onRemove={() => setFileList([])}
              maxCount={1}
              accept=".pdf,.doc,.docx,.md,.txt,.xls,.xlsx"
            >
              <Button icon={<UploadOutlined />}>选择文件</Button>
            </Upload>
            <div style={{ marginTop: 8, color: '#999', fontSize: 12 }}>
              支持格式: Word (.doc/.docx)、PDF、Markdown、Excel (.xls/.xlsx)、TXT (最大10MB)
            </div>
          </Form.Item>
        </Form>
      </Modal>

      {/* 添加外链模态框 */}
      <Modal
        title="添加外链"
        open={urlModalVisible}
        onCancel={() => {
          setUrlModalVisible(false)
          urlForm.resetFields()
        }}
        onOk={() => urlForm.submit()}
        confirmLoading={loading}
      >
        <Form form={urlForm} layout="vertical" onFinish={handleAddUrl}>
          <Form.Item
            name="name"
            label="链接名称"
            rules={[{ required: true, message: '请输入链接名称' }]}
          >
            <Input placeholder="请输入链接名称" />
          </Form.Item>

          <Form.Item
            name="type"
            label="文档类型"
            rules={[{ required: true, message: '请选择文档类型' }]}
          >
            <Select
              placeholder="请选择文档类型"
              options={[
                { label: '用例', value: 'case' },
                { label: '缺陷', value: 'defect' },
                { label: '规则', value: 'rule' },
                { label: '接口', value: 'api' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="url"
            label="URL地址"
            rules={[
              { required: true, message: '请输入URL地址' },
              { type: 'url', message: '请输入有效的URL地址' },
            ]}
          >
            <Input placeholder="https://example.com/document" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 预览抽屉 */}
      <Drawer
        title="知识库详情"
        placement="right"
        width={720}
        open={previewDrawerVisible}
        onClose={() => {
          setPreviewDrawerVisible(false)
          setSelectedKb(null)
        }}
      >
        {selectedKb && (
          <Tabs defaultActiveKey="content">
            <TabPane tab="内容" key="content">
              <Paragraph>
                <strong>名称:</strong> {selectedKb.name}
              </Paragraph>
              <Paragraph>
                <strong>类型:</strong>{' '}
                <Tag color={getTypeColor(selectedKb.type)}>
                  {getTypeText(selectedKb.type)}
                </Tag>
              </Paragraph>
              <Paragraph>
                <strong>存储方式:</strong> {selectedKb.storage_type}
              </Paragraph>
              {selectedKb.file_path && (
                <Paragraph>
                  <strong>文件路径:</strong> {selectedKb.file_path}
                </Paragraph>
              )}
              {selectedKb.url && (
                <Paragraph>
                  <strong>URL:</strong>{' '}
                  <a href={selectedKb.url} target="_blank" rel="noopener noreferrer">
                    {selectedKb.url}
                  </a>
                </Paragraph>
              )}
              <Paragraph>
                <strong>创建时间:</strong>{' '}
                {new Date(selectedKb.created_at).toLocaleString('zh-CN')}
              </Paragraph>
              <Paragraph>
                <strong>更新时间:</strong>{' '}
                {new Date(selectedKb.updated_at).toLocaleString('zh-CN')}
              </Paragraph>
              <div style={{ marginTop: 16 }}>
                <strong>文档内容:</strong>
                <div
                  style={{
                    marginTop: 8,
                    padding: 12,
                    background: '#f5f5f5',
                    borderRadius: 4,
                    maxHeight: 400,
                    overflow: 'auto',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {selectedKb.content || '无内容'}
                </div>
              </div>
            </TabPane>
            <TabPane tab="元数据" key="metadata">
              <pre style={{ background: '#f5f5f5', padding: 12, borderRadius: 4 }}>
                {JSON.stringify(selectedKb.metadata || {}, null, 2)}
              </pre>
            </TabPane>
          </Tabs>
        )}
      </Drawer>
    </div>
  )
}

export default KnowledgeBasePage
