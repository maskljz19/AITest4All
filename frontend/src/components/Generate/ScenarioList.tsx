/**
 * Scenario List Component
 * 场景列表组件 - 场景卡片、分类展示、选择、删除
 */
import React, { useState } from 'react'
import {
  Card,
  Row,
  Col,
  Tag,
  Checkbox,
  Button,
  Space,
  Modal,
  Input,
  message,
  Divider,
  Empty,
} from 'antd'
import {
  DeleteOutlined,
  PlusOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons'
import { Scenario } from '@/types'

const { TextArea } = Input

interface ScenarioListProps {
  scenarios: Scenario[]
  selectedIds: string[]
  onSelectionChange: (ids: string[]) => void
  onDelete: (id: string) => void
  onSupplement: (instruction: string) => void
  loading?: boolean
}

const categoryColors: Record<string, string> = {
  normal: 'green',
  exception: 'red',
  boundary: 'orange',
  performance: 'blue',
  security: 'purple',
  compatibility: 'cyan',
  interaction: 'magenta',
}

const categoryLabels: Record<string, string> = {
  normal: '正常场景',
  exception: '异常场景',
  boundary: '边界场景',
  performance: '性能场景',
  security: '安全场景',
  compatibility: '兼容性场景',
  interaction: '交互场景',
}

const ScenarioList: React.FC<ScenarioListProps> = ({
  scenarios,
  selectedIds,
  onSelectionChange,
  onDelete,
  onSupplement,
  loading = false,
}) => {
  const [supplementModalVisible, setSupplementModalVisible] = useState(false)
  const [supplementInstruction, setSupplementInstruction] = useState('')

  // Group scenarios by category
  const groupedScenarios = scenarios.reduce((acc, scenario) => {
    const category = scenario.category || 'normal'
    if (!acc[category]) {
      acc[category] = []
    }
    acc[category].push(scenario)
    return acc
  }, {} as Record<string, Scenario[]>)

  const handleSelectAll = () => {
    if (selectedIds.length === scenarios.length) {
      onSelectionChange([])
    } else {
      onSelectionChange(scenarios.map((s) => s.scenario_id))
    }
  }

  const handleSelectScenario = (id: string, checked: boolean) => {
    if (checked) {
      onSelectionChange([...selectedIds, id])
    } else {
      onSelectionChange(selectedIds.filter((sid) => sid !== id))
    }
  }

  const handleDeleteScenario = (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个场景吗？',
      onOk: () => {
        onDelete(id)
        message.success('删除成功')
      },
    })
  }

  const handleSupplement = () => {
    if (!supplementInstruction.trim()) {
      message.error('请输入补充说明')
      return
    }
    onSupplement(supplementInstruction)
    setSupplementModalVisible(false)
    setSupplementInstruction('')
  }

  if (scenarios.length === 0) {
    return (
      <Card title="测试场景" bordered={false}>
        <Empty description="暂无场景数据" />
      </Card>
    )
  }

  return (
    <>
      <Card
        title={
          <Space>
            <span>测试场景</span>
            <Tag color="blue">
              已选择 {selectedIds.length} / {scenarios.length}
            </Tag>
          </Space>
        }
        bordered={false}
        extra={
          <Space>
            <Button onClick={handleSelectAll} disabled={loading}>
              {selectedIds.length === scenarios.length ? '取消全选' : '全选'}
            </Button>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setSupplementModalVisible(true)}
              disabled={loading}
            >
              补充场景
            </Button>
          </Space>
        }
      >
        {Object.entries(groupedScenarios).map(([category, categoryScenarios]) => (
          <div key={category} style={{ marginBottom: 24 }}>
            <Divider orientation="left">
              <Tag color={categoryColors[category] || 'default'}>
                {categoryLabels[category] || category}
              </Tag>
            </Divider>
            <Row gutter={[16, 16]}>
              {categoryScenarios.map((scenario) => {
                const isSelected = selectedIds.includes(scenario.scenario_id)
                return (
                  <Col xs={24} sm={12} lg={8} key={scenario.scenario_id}>
                    <Card
                      size="small"
                      hoverable
                      style={{
                        borderColor: isSelected ? '#1890ff' : undefined,
                        borderWidth: isSelected ? 2 : 1,
                      }}
                      bodyStyle={{ padding: 16 }}
                    >
                      <Space direction="vertical" style={{ width: '100%' }} size="small">
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Checkbox
                            checked={isSelected}
                            onChange={(e) =>
                              handleSelectScenario(scenario.scenario_id, e.target.checked)
                            }
                            disabled={loading}
                          >
                            <strong>{scenario.name}</strong>
                          </Checkbox>
                          <Button
                            type="text"
                            danger
                            size="small"
                            icon={<DeleteOutlined />}
                            onClick={() => handleDeleteScenario(scenario.scenario_id)}
                            disabled={loading}
                          />
                        </div>

                        <div style={{ fontSize: 12, color: '#666' }}>
                          <div style={{ marginBottom: 4 }}>
                            <Tag>{scenario.scenario_id}</Tag>
                            <Tag color={scenario.priority === 'P0' ? 'red' : 'default'}>
                              {scenario.priority}
                            </Tag>
                          </div>
                          <div style={{ marginBottom: 8 }}>{scenario.description}</div>
                          <div>
                            <ExclamationCircleOutlined style={{ marginRight: 4 }} />
                            前置条件: {scenario.precondition}
                          </div>
                          <div>
                            <CheckCircleOutlined style={{ marginRight: 4 }} />
                            预期结果: {scenario.expected_result}
                          </div>
                        </div>
                      </Space>
                    </Card>
                  </Col>
                )
              })}
            </Row>
          </div>
        ))}
      </Card>

      <Modal
        title="补充测试场景"
        open={supplementModalVisible}
        onOk={handleSupplement}
        onCancel={() => {
          setSupplementModalVisible(false)
          setSupplementInstruction('')
        }}
        confirmLoading={loading}
      >
        <TextArea
          rows={6}
          placeholder="请描述需要补充的场景，例如：需要增加并发登录的测试场景"
          value={supplementInstruction}
          onChange={(e) => setSupplementInstruction(e.target.value)}
        />
      </Modal>
    </>
  )
}

export default ScenarioList
