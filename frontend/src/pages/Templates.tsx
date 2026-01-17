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
  message,
  Tag,
  Popconfirm,
  Drawer,
  Typography,
  Tabs,
  Alert,
} from 'antd'
import {
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  ReloadOutlined,
  CopyOutlined,
} from '@ant-design/icons'
import Editor from '@monaco-editor/react'
import { templatesApi } from '../api/templates'

const { Paragraph } = Typography
const { TabPane } = Tabs

interface Template {
  id: number
  name: string
  test_type: 'ui' | 'api' | 'unit'
  template_structure: Record<string, any>
  is_builtin: boolean
  created_at: string
  updated_at: string
}

const TemplatesPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [dataSource, setDataSource] = useState<Template[]>([])
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [previewDrawerVisible, setPreviewDrawerVisible] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [filterType, setFilterType] = useState<string>('all')

  const [editForm] = Form.useForm()

  // 默认模板结构
  const defaultTemplateStructure = {
    case_id: '用例ID',
    title: '用例标题',
    test_type: '测试类型',
    priority: '优先级',
    precondition: '前置条件',
    steps: [
      {
        step_no: 1,
        action: '操作步骤',
        data: '测试数据',
        expected: '预期结果',
      },
    ],
    test_data: {},
    expected_result: '预期结果',
    postcondition: '后置条件',
  }

  // 加载模板列表
  const loadTemplates = async () => {
    setLoading(true)
    try {
      const params = filterType === 'all' ? {} : { test_type: filterType }
      const response = await templatesApi.getList(params)
      setDataSource(Array.isArray(response.data.data) ? response.data.data : [])
    } catch (error: any) {
      message.error(error.response?.data?.message || '加载模板列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadTemplates()
  }, [filterType])

  // 创建/更新模板
  const handleSaveTemplate = async (values: any) => {
    setLoading(true)
    try {
      let templateStructure
      try {
        templateStructure = JSON.parse(values.template_structure)
      } catch (e) {
        message.error('模板结构JSON格式错误')
        setLoading(false)
        return
      }

      const data = {
        name: values.name,
        test_type: values.test_type,
        template_structure: templateStructure,
      }

      if (isEditing && selectedTemplate) {
        await templatesApi.update(selectedTemplate.id, data)
        message.success('更新成功')
      } else {
        await templatesApi.create(data)
        message.success('创建成功')
      }

      setEditModalVisible(false)
      editForm.resetFields()
      setSelectedTemplate(null)
      setIsEditing(false)
      loadTemplates()
    } catch (error: any) {
      message.error(error.response?.data?.message || '保存失败')
    } finally {
      setLoading(false)
    }
  }

  // 删除模板
  const handleDelete = async (id: number) => {
    setLoading(true)
    try {
      await templatesApi.delete(id)
      message.success('删除成功')
      loadTemplates()
    } catch (error: any) {
      message.error(error.response?.data?.message || '删除失败')
    } finally {
      setLoading(false)
    }
  }

  // 打开编辑模态框
  const handleEdit = async (record: Template) => {
    setLoading(true)
    try {
      const response = await templatesApi.getDetail(record.id)
      const template = response.data
      setSelectedTemplate(template)
      setIsEditing(true)
      editForm.setFieldsValue({
        name: template.name,
        test_type: template.test_type,
        template_structure: JSON.stringify(template.template_structure, null, 2),
      })
      setEditModalVisible(true)
    } catch (error: any) {
      message.error(error.response?.data?.message || '加载模板详情失败')
    } finally {
      setLoading(false)
    }
  }

  // 打开创建模态框
  const handleCreate = () => {
    setSelectedTemplate(null)
    setIsEditing(false)
    editForm.resetFields()
    editForm.setFieldsValue({
      template_structure: JSON.stringify(defaultTemplateStructure, null, 2),
    })
    setEditModalVisible(true)
  }

  // 复制模板
  const handleCopy = async (record: Template) => {
    setLoading(true)
    try {
      const response = await templatesApi.getDetail(record.id)
      const template = response.data
      setSelectedTemplate(null)
      setIsEditing(false)
      editForm.setFieldsValue({
        name: `${template.name} (副本)`,
        test_type: template.test_type,
        template_structure: JSON.stringify(template.template_structure, null, 2),
      })
      setEditModalVisible(true)
    } catch (error: any) {
      message.error(error.response?.data?.message || '加载模板详情失败')
    } finally {
      setLoading(false)
    }
  }

  // 预览模板
  const handlePreview = async (record: Template) => {
    setLoading(true)
    try {
      const response = await templatesApi.getDetail(record.id)
      setSelectedTemplate(response.data)
      setPreviewDrawerVisible(true)
    } catch (error: any) {
      message.error(error.response?.data?.message || '加载详情失败')
    } finally {
      setLoading(false)
    }
  }

  // 测试类型标签颜色
  const getTestTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      ui: 'blue',
      api: 'green',
      unit: 'orange',
    }
    return colors[type] || 'default'
  }

  // 测试类型标签文本
  const getTestTypeText = (type: string) => {
    const texts: Record<string, string> = {
      ui: 'UI测试',
      api: '接口测试',
      unit: '单元测试',
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
      title: '模板名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: '测试类型',
      dataIndex: 'test_type',
      key: 'test_type',
      width: 120,
      render: (type: string) => (
        <Tag color={getTestTypeColor(type)}>{getTestTypeText(type)}</Tag>
      ),
    },
    {
      title: '类型',
      dataIndex: 'is_builtin',
      key: 'is_builtin',
      width: 100,
      render: (isBuiltin: boolean) => (
        <Tag color={isBuiltin ? 'green' : 'default'}>
          {isBuiltin ? '内置' : '自定义'}
        </Tag>
      ),
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
      width: 250,
      render: (_: any, record: Template) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handlePreview(record)}
          >
            预览
          </Button>
          <Button
            type="link"
            size="small"
            icon={<CopyOutlined />}
            onClick={() => handleCopy(record)}
          >
            复制
          </Button>
          {!record.is_builtin && (
            <>
              <Button
                type="link"
                size="small"
                icon={<EditOutlined />}
                onClick={() => handleEdit(record)}
              >
                编辑
              </Button>
              <Popconfirm
                title="确定删除此模板吗？"
                onConfirm={() => handleDelete(record.id)}
                okText="确定"
                cancelText="取消"
              >
                <Button type="link" size="small" danger icon={<DeleteOutlined />}>
                  删除
                </Button>
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>模板管理</h1>

      <Card>
        <Alert
          message="模板说明"
          description="用例模板定义了测试用例的结构和字段。创建模板时需要提供JSON格式的模板结构。"
          type="info"
          showIcon
          style={{ marginBottom: 16 }}
        />

        {/* 操作栏 */}
        <Space style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            创建模板
          </Button>
          <Button icon={<ReloadOutlined />} onClick={loadTemplates}>
            刷新
          </Button>
          <Select
            style={{ width: 150 }}
            value={filterType}
            onChange={setFilterType}
            options={[
              { label: '全部类型', value: 'all' },
              { label: 'UI测试', value: 'ui' },
              { label: '接口测试', value: 'api' },
              { label: '单元测试', value: 'unit' },
            ]}
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

      {/* 编辑/创建模态框 */}
      <Modal
        title={isEditing ? '编辑模板' : '创建模板'}
        open={editModalVisible}
        onCancel={() => {
          setEditModalVisible(false)
          editForm.resetFields()
          setSelectedTemplate(null)
          setIsEditing(false)
        }}
        onOk={() => editForm.submit()}
        confirmLoading={loading}
        width={900}
      >
        <Form form={editForm} layout="vertical" onFinish={handleSaveTemplate}>
          <Form.Item
            name="name"
            label="模板名称"
            rules={[{ required: true, message: '请输入模板名称' }]}
          >
            <Input placeholder="请输入模板名称" />
          </Form.Item>

          <Form.Item
            name="test_type"
            label="测试类型"
            rules={[{ required: true, message: '请选择测试类型' }]}
          >
            <Select
              placeholder="请选择测试类型"
              options={[
                { label: 'UI测试', value: 'ui' },
                { label: '接口测试', value: 'api' },
                { label: '单元测试', value: 'unit' },
              ]}
            />
          </Form.Item>

          <Form.Item
            name="template_structure"
            label="模板结构 (JSON格式)"
            rules={[{ required: true, message: '请输入模板结构' }]}
            tooltip="定义测试用例的字段结构，必须是有效的JSON格式"
          >
            <Editor
              height="400px"
              defaultLanguage="json"
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true,
                formatOnPaste: true,
                formatOnType: true,
              }}
              onChange={(value) =>
                editForm.setFieldValue('template_structure', value)
              }
            />
          </Form.Item>

          <Alert
            message="模板结构示例"
            description={
              <pre style={{ margin: 0, fontSize: 12 }}>
                {JSON.stringify(defaultTemplateStructure, null, 2)}
              </pre>
            }
            type="info"
            showIcon
          />
        </Form>
      </Modal>

      {/* 预览抽屉 */}
      <Drawer
        title="模板详情"
        placement="right"
        width={720}
        open={previewDrawerVisible}
        onClose={() => {
          setPreviewDrawerVisible(false)
          setSelectedTemplate(null)
        }}
      >
        {selectedTemplate && (
          <Tabs defaultActiveKey="structure">
            <TabPane tab="模板结构" key="structure">
              <Paragraph>
                <strong>名称:</strong> {selectedTemplate.name}
              </Paragraph>
              <Paragraph>
                <strong>测试类型:</strong>{' '}
                <Tag color={getTestTypeColor(selectedTemplate.test_type)}>
                  {getTestTypeText(selectedTemplate.test_type)}
                </Tag>
              </Paragraph>
              <Paragraph>
                <strong>类型:</strong>{' '}
                <Tag color={selectedTemplate.is_builtin ? 'green' : 'default'}>
                  {selectedTemplate.is_builtin ? '内置' : '自定义'}
                </Tag>
              </Paragraph>
              <Paragraph>
                <strong>创建时间:</strong>{' '}
                {new Date(selectedTemplate.created_at).toLocaleString('zh-CN')}
              </Paragraph>
              <Paragraph>
                <strong>更新时间:</strong>{' '}
                {new Date(selectedTemplate.updated_at).toLocaleString('zh-CN')}
              </Paragraph>
              <div style={{ marginTop: 16 }}>
                <strong>模板结构:</strong>
                <Editor
                  height="400px"
                  defaultLanguage="json"
                  value={JSON.stringify(selectedTemplate.template_structure, null, 2)}
                  theme="vs-dark"
                  options={{
                    readOnly: true,
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: 'on',
                    scrollBeyondLastLine: false,
                  }}
                />
              </div>
            </TabPane>
            <TabPane tab="字段说明" key="fields">
              <div style={{ padding: '16px 0' }}>
                <Paragraph>
                  <strong>模板字段说明:</strong>
                </Paragraph>
                <ul style={{ lineHeight: 2 }}>
                  <li>
                    <strong>case_id:</strong> 用例ID，唯一标识
                  </li>
                  <li>
                    <strong>title:</strong> 用例标题
                  </li>
                  <li>
                    <strong>test_type:</strong> 测试类型 (ui/api/unit)
                  </li>
                  <li>
                    <strong>priority:</strong> 优先级 (P0/P1/P2/P3)
                  </li>
                  <li>
                    <strong>precondition:</strong> 前置条件
                  </li>
                  <li>
                    <strong>steps:</strong> 测试步骤数组
                    <ul>
                      <li>step_no: 步骤编号</li>
                      <li>action: 操作步骤</li>
                      <li>data: 测试数据</li>
                      <li>expected: 预期结果</li>
                    </ul>
                  </li>
                  <li>
                    <strong>test_data:</strong> 测试数据对象
                  </li>
                  <li>
                    <strong>expected_result:</strong> 预期结果
                  </li>
                  <li>
                    <strong>postcondition:</strong> 后置条件
                  </li>
                </ul>
              </div>
            </TabPane>
          </Tabs>
        )}
      </Drawer>
    </div>
  )
}

export default TemplatesPage
