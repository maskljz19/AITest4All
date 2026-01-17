/**
 * Test Case List Component
 * 测试用例列表组件 - 表格展示、详情展开、编辑、选择、对话优化
 */
import React, { useState } from 'react'
import {
  Card,
  Table,
  Tag,
  Button,
  Space,
  Modal,
  Input,
  Form,
  message,
  Descriptions,
  Checkbox,
} from 'antd'
import { EditOutlined, MessageOutlined } from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { TestCase } from '@/types'

const { TextArea } = Input

interface TestCaseListProps {
  testCases: TestCase[]
  selectedIds: string[]
  onSelectionChange: (ids: string[]) => void
  onUpdate: (caseId: string, data: TestCase) => void
  onOptimize: (selectedIds: string[], instruction: string) => void
  loading?: boolean
}

const TestCaseList: React.FC<TestCaseListProps> = ({
  testCases,
  selectedIds,
  onSelectionChange,
  onUpdate,
  onOptimize,
  loading = false,
}) => {
  const [editModalVisible, setEditModalVisible] = useState(false)
  const [optimizeModalVisible, setOptimizeModalVisible] = useState(false)
  const [currentCase, setCurrentCase] = useState<TestCase | null>(null)
  const [optimizeInstruction, setOptimizeInstruction] = useState('')
  const [form] = Form.useForm()

  const handleEdit = (testCase: TestCase) => {
    setCurrentCase(testCase)
    form.setFieldsValue({
      title: testCase.title,
      priority: testCase.priority,
      precondition: testCase.precondition,
      expected_result: testCase.expected_result,
      postcondition: testCase.postcondition,
      test_data: JSON.stringify(testCase.test_data, null, 2),
    })
    setEditModalVisible(true)
  }

  const handleSaveEdit = () => {
    form.validateFields().then((values) => {
      if (!currentCase) return

      try {
        const updatedCase: TestCase = {
          ...currentCase,
          title: values.title,
          priority: values.priority,
          precondition: values.precondition,
          expected_result: values.expected_result,
          postcondition: values.postcondition,
          test_data: JSON.parse(values.test_data),
        }
        onUpdate(currentCase.case_id, updatedCase)
        setEditModalVisible(false)
        message.success('保存成功')
      } catch (error) {
        message.error('测试数据格式错误，请检查JSON格式')
      }
    })
  }

  const handleOptimize = () => {
    if (selectedIds.length === 0) {
      message.error('请先选择要优化的用例')
      return
    }
    if (!optimizeInstruction.trim()) {
      message.error('请输入优化指令')
      return
    }
    onOptimize(selectedIds, optimizeInstruction)
    setOptimizeModalVisible(false)
    setOptimizeInstruction('')
  }

  const columns: ColumnsType<TestCase> = [
    {
      title: '选择',
      key: 'select',
      width: 60,
      render: (_, record) => (
        <Checkbox
          checked={selectedIds.includes(record.case_id)}
          onChange={(e) => {
            if (e.target.checked) {
              onSelectionChange([...selectedIds, record.case_id])
            } else {
              onSelectionChange(selectedIds.filter((id) => id !== record.case_id))
            }
          }}
          disabled={loading}
        />
      ),
    },
    {
      title: '用例ID',
      dataIndex: 'case_id',
      key: 'case_id',
      width: 100,
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '类型',
      dataIndex: 'test_type',
      key: 'test_type',
      width: 80,
      render: (type: string) => {
        const colorMap: Record<string, string> = {
          ui: 'blue',
          api: 'green',
          unit: 'orange',
        }
        return <Tag color={colorMap[type]}>{type.toUpperCase()}</Tag>
      },
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority: string) => {
        const color = priority === 'P0' ? 'red' : priority === 'P1' ? 'orange' : 'default'
        return <Tag color={color}>{priority}</Tag>
      },
    },
    {
      title: '步骤数',
      key: 'steps',
      width: 80,
      render: (_, record) => record.steps.length,
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button
          type="link"
          icon={<EditOutlined />}
          onClick={() => handleEdit(record)}
          disabled={loading}
        >
          编辑
        </Button>
      ),
    },
  ]

  const expandedRowRender = (record: TestCase) => {
    return (
      <div style={{ padding: '16px 24px' }}>
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="前置条件">{record.precondition}</Descriptions.Item>
          <Descriptions.Item label="测试步骤">
            <ol style={{ margin: 0, paddingLeft: 20 }}>
              {record.steps.map((step) => (
                <li key={step.step_no} style={{ marginBottom: 8 }}>
                  <div>
                    <strong>操作:</strong> {step.action}
                  </div>
                  {step.data && (
                    <div>
                      <strong>数据:</strong>{' '}
                      {typeof step.data === 'string'
                        ? step.data
                        : JSON.stringify(step.data, null, 2)}
                    </div>
                  )}
                  <div>
                    <strong>预期:</strong> {step.expected}
                  </div>
                </li>
              ))}
            </ol>
          </Descriptions.Item>
          <Descriptions.Item label="测试数据">
            <pre style={{ margin: 0, fontSize: 12 }}>
              {JSON.stringify(record.test_data, null, 2)}
            </pre>
          </Descriptions.Item>
          <Descriptions.Item label="预期结果">{record.expected_result}</Descriptions.Item>
          <Descriptions.Item label="后置条件">{record.postcondition}</Descriptions.Item>
        </Descriptions>
      </div>
    )
  }

  return (
    <>
      <Card
        title={
          <Space>
            <span>测试用例</span>
            <Tag color="blue">
              已选择 {selectedIds.length} / {testCases.length}
            </Tag>
          </Space>
        }
        bordered={false}
        extra={
          <Space>
            <Button
              onClick={() => {
                if (selectedIds.length === testCases.length) {
                  onSelectionChange([])
                } else {
                  onSelectionChange(testCases.map((c) => c.case_id))
                }
              }}
              disabled={loading}
            >
              {selectedIds.length === testCases.length ? '取消全选' : '全选'}
            </Button>
            <Button
              type="primary"
              icon={<MessageOutlined />}
              onClick={() => setOptimizeModalVisible(true)}
              disabled={loading || selectedIds.length === 0}
            >
              对话优化
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={testCases}
          rowKey="case_id"
          expandable={{
            expandedRowRender,
          }}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
          loading={loading}
        />
      </Card>

      {/* Edit Modal */}
      <Modal
        title="编辑测试用例"
        open={editModalVisible}
        onOk={handleSaveEdit}
        onCancel={() => setEditModalVisible(false)}
        width={800}
        confirmLoading={loading}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="标题" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="priority" label="优先级" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="precondition" label="前置条件">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item name="expected_result" label="预期结果">
            <TextArea rows={3} />
          </Form.Item>
          <Form.Item name="postcondition" label="后置条件">
            <TextArea rows={2} />
          </Form.Item>
          <Form.Item name="test_data" label="测试数据 (JSON格式)">
            <TextArea rows={6} />
          </Form.Item>
        </Form>
      </Modal>

      {/* Optimize Modal */}
      <Modal
        title="对话优化用例"
        open={optimizeModalVisible}
        onOk={handleOptimize}
        onCancel={() => {
          setOptimizeModalVisible(false)
          setOptimizeInstruction('')
        }}
        confirmLoading={loading}
      >
        <div style={{ marginBottom: 16 }}>
          <Tag color="blue">已选择 {selectedIds.length} 个用例</Tag>
        </div>
        <TextArea
          rows={6}
          placeholder="请描述优化需求，例如：增加更详细的测试步骤，补充边界值测试数据"
          value={optimizeInstruction}
          onChange={(e) => setOptimizeInstruction(e.target.value)}
        />
      </Modal>
    </>
  )
}

export default TestCaseList
