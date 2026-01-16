import React, { useState, useEffect } from 'react'
import {
  Card,
  Button,
  Table,
  Space,
  Modal,
  Form,
  Input,
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
  PlayCircleOutlined,
  ReloadOutlined,
  CodeOutlined,
} from '@ant-design/icons'
import Editor from '@monaco-editor/react'
import { scriptsApi } from '../api/scripts'

const { TextArea } = Input
const { Paragraph, Text } = Typography
const { TabPane } = Tabs

interface Script {
  id: number
  name: string
  description?: string
  code: string
  dependencies?: string[]
  is_builtin: boolean
  created_at: string
  updated_at: string
}

const ScriptsPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [dataSource, setDataSource] = useState<Script[]>([])
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [testModalVisible, setTestModalVisible] = useState(false)
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false)
  const [selectedScript, setSelectedScript] = useState<Script | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [testResult, setTestResult] = useState<any>(null)
  const [testLoading, setTestLoading] = useState(false)

  const [editForm] = Form.useForm()
  const [testForm] = Form.useForm()

  // 加载脚本列表
  const loadScripts = async () => {
    setLoading(true)
    try {
      const response = await scriptsApi.getList()
      setDataSource(response.data || [])
    } catch (error: any) {
      message.error(error.response?.data?.message || '加载脚本列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadScripts()
  }, [])

  // 创建/更新脚本
  const handleSaveScript = async (values: any) => {
    setLoading(true)
    try {
      const data = {
        name: values.name,
        description: values.description,
        code: values.code,
        dependencies: values.dependencies
          ? values.dependencies.split(',').map((d: string) => d.trim()).filter(Boolean)
          : [],
      }

      if (isEditing && selectedScript) {
        await scriptsApi.update(selectedScript.id, data)
        message.success('更新成功')
      } else {
        await scriptsApi.create(data)
        message.success('创建成功')
      }

      setEditModalVisible(false)
      editForm.resetFields()
      setSelectedScript(null)
      setIsEditing(false)
      loadScripts()
    } catch (error: any) {
      message.error(error.response?.data?.message || '保存失败')
    } finally {
      setLoading(false)
    }
  }

  // 删除脚本
  const handleDelete = async (id: number) => {
    setLoading(true)
    try {
      await scriptsApi.delete(id)
      message.success('删除成功')
      loadScripts()
    } catch (error: any) {
      message.error(error.response?.data?.message || '删除失败')
    } finally {
      setLoading(false)
    }
  }

  // 打开编辑模态框
  const handleEdit = async (record: Script) => {
    setLoading(true)
    try {
      const response = await scriptsApi.getDetail(record.id)
      const script = response.data
      setSelectedScript(script)
      setIsEditing(true)
      editForm.setFieldsValue({
        name: script.name,
        description: script.description,
        code: script.code,
        dependencies: script.dependencies?.join(', ') || '',
      })
      setEditModalVisible(true)
    } catch (error: any) {
      message.error(error.response?.data?.message || '加载脚本详情失败')
    } finally {
      setLoading(false)
    }
  }

  // 打开创建模态框
  const handleCreate = () => {
    setSelectedScript(null)
    setIsEditing(false)
    editForm.resetFields()
    editForm.setFieldsValue({
      code: `def main():\n    """脚本主函数"""\n    # 在这里编写你的代码\n    return "Hello, World!"\n\nif __name__ == "__main__":\n    result = main()\n    print(result)`,
    })
    setEditModalVisible(true)
  }

  // 测试脚本
  const handleTest = async (record: Script) => {
    setSelectedScript(record)
    setTestResult(null)
    testForm.resetFields()
    setTestModalVisible(true)
  }

  // 执行测试
  const handleRunTest = async (values: any) => {
    if (!selectedScript) return

    setTestLoading(true)
    setTestResult(null)
    try {
      const args = values.args ? JSON.parse(values.args) : {}
      const response = await scriptsApi.test(selectedScript.id, { args })
      setTestResult(response.data)
      message.success('执行成功')
    } catch (error: any) {
      const errorData = error.response?.data
      setTestResult({
        success: false,
        error: errorData?.message || '执行失败',
        output: errorData?.output || '',
      })
      message.error(errorData?.message || '执行失败')
    } finally {
      setTestLoading(false)
    }
  }

  // 查看详情
  const handleViewDetail = async (record: Script) => {
    setLoading(true)
    try {
      const response = await scriptsApi.getDetail(record.id)
      setSelectedScript(response.data)
      setDetailDrawerVisible(true)
    } catch (error: any) {
      message.error(error.response?.data?.message || '加载详情失败')
    } finally {
      setLoading(false)
    }
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
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '依赖',
      dataIndex: 'dependencies',
      key: 'dependencies',
      width: 200,
      render: (deps: string[]) =>
        deps && deps.length > 0 ? (
          <Space wrap>
            {deps.map((dep, idx) => (
              <Tag key={idx} color="blue">
                {dep}
              </Tag>
            ))}
          </Space>
        ) : (
          <Text type="secondary">无</Text>
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
      width: 220,
      render: (_: any, record: Script) => (
        <Space>
          <Button
            type="link"
            size="small"
            icon={<CodeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => handleTest(record)}
          >
            测试
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
                title="确定删除此脚本吗？"
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
      <h1 style={{ marginBottom: 24 }}>脚本管理</h1>

      <Card>
        {/* 操作栏 */}
        <Space style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            创建脚本
          </Button>
          <Button icon={<ReloadOutlined />} onClick={loadScripts}>
            刷新
          </Button>
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
        title={isEditing ? '编辑脚本' : '创建脚本'}
        open={editModalVisible}
        onCancel={() => {
          setEditModalVisible(false)
          editForm.resetFields()
          setSelectedScript(null)
          setIsEditing(false)
        }}
        onOk={() => editForm.submit()}
        confirmLoading={loading}
        width={900}
      >
        <Form form={editForm} layout="vertical" onFinish={handleSaveScript}>
          <Form.Item
            name="name"
            label="脚本名称"
            rules={[{ required: true, message: '请输入脚本名称' }]}
          >
            <Input placeholder="请输入脚本名称" />
          </Form.Item>

          <Form.Item name="description" label="描述">
            <TextArea rows={2} placeholder="请输入脚本描述" />
          </Form.Item>

          <Form.Item
            name="code"
            label="脚本代码"
            rules={[{ required: true, message: '请输入脚本代码' }]}
          >
            <Editor
              height="400px"
              defaultLanguage="python"
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true,
              }}
              onChange={(value) => editForm.setFieldValue('code', value)}
            />
          </Form.Item>

          <Form.Item
            name="dependencies"
            label="依赖包"
            tooltip="多个依赖用逗号分隔，例如: requests, faker"
          >
            <Input placeholder="例如: requests, faker" />
          </Form.Item>
        </Form>
      </Modal>

      {/* 测试模态框 */}
      <Modal
        title={`测试脚本: ${selectedScript?.name || ''}`}
        open={testModalVisible}
        onCancel={() => {
          setTestModalVisible(false)
          setTestResult(null)
          testForm.resetFields()
        }}
        footer={[
          <Button
            key="close"
            onClick={() => {
              setTestModalVisible(false)
              setTestResult(null)
              testForm.resetFields()
            }}
          >
            关闭
          </Button>,
          <Button
            key="run"
            type="primary"
            loading={testLoading}
            onClick={() => testForm.submit()}
          >
            执行
          </Button>,
        ]}
        width={800}
      >
        <Form form={testForm} layout="vertical" onFinish={handleRunTest}>
          <Form.Item
            name="args"
            label="参数 (JSON格式)"
            tooltip="输入JSON格式的参数，例如: {}"
          >
            <TextArea
              rows={4}
              placeholder='{"key": "value"}'
              style={{ fontFamily: 'monospace' }}
            />
          </Form.Item>
        </Form>

        {testResult && (
          <div style={{ marginTop: 16 }}>
            <Alert
              message={testResult.success !== false ? '执行成功' : '执行失败'}
              type={testResult.success !== false ? 'success' : 'error'}
              showIcon
              style={{ marginBottom: 16 }}
            />
            <div>
              <strong>输出结果:</strong>
              <pre
                style={{
                  marginTop: 8,
                  padding: 12,
                  background: '#f5f5f5',
                  borderRadius: 4,
                  maxHeight: 300,
                  overflow: 'auto',
                }}
              >
                {testResult.output || testResult.error || JSON.stringify(testResult, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </Modal>

      {/* 详情抽屉 */}
      <Drawer
        title="脚本详情"
        placement="right"
        width={800}
        open={detailDrawerVisible}
        onClose={() => {
          setDetailDrawerVisible(false)
          setSelectedScript(null)
        }}
      >
        {selectedScript && (
          <Tabs defaultActiveKey="code">
            <TabPane tab="代码" key="code">
              <Paragraph>
                <strong>名称:</strong> {selectedScript.name}
              </Paragraph>
              <Paragraph>
                <strong>描述:</strong> {selectedScript.description || '无'}
              </Paragraph>
              <Paragraph>
                <strong>类型:</strong>{' '}
                <Tag color={selectedScript.is_builtin ? 'green' : 'default'}>
                  {selectedScript.is_builtin ? '内置' : '自定义'}
                </Tag>
              </Paragraph>
              {selectedScript.dependencies && selectedScript.dependencies.length > 0 && (
                <Paragraph>
                  <strong>依赖:</strong>{' '}
                  <Space wrap>
                    {selectedScript.dependencies.map((dep, idx) => (
                      <Tag key={idx} color="blue">
                        {dep}
                      </Tag>
                    ))}
                  </Space>
                </Paragraph>
              )}
              <div style={{ marginTop: 16 }}>
                <strong>代码:</strong>
                <Editor
                  height="500px"
                  defaultLanguage="python"
                  value={selectedScript.code}
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
            <TabPane tab="信息" key="info">
              <Paragraph>
                <strong>ID:</strong> {selectedScript.id}
              </Paragraph>
              <Paragraph>
                <strong>名称:</strong> {selectedScript.name}
              </Paragraph>
              <Paragraph>
                <strong>描述:</strong> {selectedScript.description || '无'}
              </Paragraph>
              <Paragraph>
                <strong>类型:</strong>{' '}
                <Tag color={selectedScript.is_builtin ? 'green' : 'default'}>
                  {selectedScript.is_builtin ? '内置' : '自定义'}
                </Tag>
              </Paragraph>
              <Paragraph>
                <strong>创建时间:</strong>{' '}
                {new Date(selectedScript.created_at).toLocaleString('zh-CN')}
              </Paragraph>
              <Paragraph>
                <strong>更新时间:</strong>{' '}
                {new Date(selectedScript.updated_at).toLocaleString('zh-CN')}
              </Paragraph>
            </TabPane>
          </Tabs>
        )}
      </Drawer>
    </div>
  )
}

export default ScriptsPage
