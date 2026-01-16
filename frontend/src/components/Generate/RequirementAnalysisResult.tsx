/**
 * Requirement Analysis Result Component
 * 需求分析结果展示组件 - 可折叠面板、在线编辑
 */
import React, { useState } from 'react'
import { Card, Collapse, Tag, Button, Space, Input, message, Typography } from 'antd'
import { EditOutlined, SaveOutlined, CloseOutlined, ReloadOutlined } from '@ant-design/icons'
import { RequirementAnalysis } from '@/types'

const { Panel } = Collapse
const { TextArea } = Input
const { Title, Paragraph } = Typography

interface RequirementAnalysisResultProps {
  data: RequirementAnalysis
  onUpdate: (data: RequirementAnalysis) => void
  onReanalyze: () => void
  loading?: boolean
}

const RequirementAnalysisResult: React.FC<RequirementAnalysisResultProps> = ({
  data,
  onUpdate,
  onReanalyze,
  loading = false,
}) => {
  const [editing, setEditing] = useState(false)
  const [editData, setEditData] = useState<RequirementAnalysis>(data)

  const handleEdit = () => {
    setEditData(data)
    setEditing(true)
  }

  const handleSave = () => {
    onUpdate(editData)
    setEditing(false)
    message.success('保存成功')
  }

  const handleCancel = () => {
    setEditData(data)
    setEditing(false)
  }

  const renderStringList = (
    list: string[],
    field: keyof RequirementAnalysis,
    title: string
  ) => {
    if (editing) {
      return (
        <div>
          <Title level={5}>{title}</Title>
          <TextArea
            value={list.join('\n')}
            onChange={(e) => {
              const newList = e.target.value.split('\n').filter((item) => item.trim())
              setEditData({ ...editData, [field]: newList })
            }}
            rows={Math.max(3, list.length)}
            placeholder={`每行一个${title}`}
          />
        </div>
      )
    }

    return (
      <div>
        <Title level={5}>{title}</Title>
        {list.length > 0 ? (
          <ul style={{ paddingLeft: 20 }}>
            {list.map((item, index) => (
              <li key={index} style={{ marginBottom: 8 }}>
                {item}
              </li>
            ))}
          </ul>
        ) : (
          <Paragraph type="secondary">暂无数据</Paragraph>
        )}
      </div>
    )
  }

  const renderDataModels = () => {
    if (editing) {
      return (
        <div>
          <Title level={5}>数据模型</Title>
          <TextArea
            value={JSON.stringify(editData.data_models, null, 2)}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value)
                setEditData({ ...editData, data_models: parsed })
              } catch (error) {
                // Invalid JSON, ignore
              }
            }}
            rows={10}
            placeholder='[{"entity": "User", "fields": ["id", "name"]}]'
          />
        </div>
      )
    }

    return (
      <div>
        <Title level={5}>数据模型</Title>
        {data.data_models.length > 0 ? (
          <div>
            {data.data_models.map((model, index) => (
              <div key={index} style={{ marginBottom: 16 }}>
                <Tag color="blue">{model.entity}</Tag>
                <div style={{ marginTop: 8, paddingLeft: 20 }}>
                  {model.fields.map((field, idx) => (
                    <Tag key={idx} style={{ marginBottom: 4 }}>
                      {field}
                    </Tag>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <Paragraph type="secondary">暂无数据</Paragraph>
        )}
      </div>
    )
  }

  const renderApiDefinitions = () => {
    if (editing) {
      return (
        <div>
          <Title level={5}>接口定义</Title>
          <TextArea
            value={JSON.stringify(editData.api_definitions, null, 2)}
            onChange={(e) => {
              try {
                const parsed = JSON.parse(e.target.value)
                setEditData({ ...editData, api_definitions: parsed })
              } catch (error) {
                // Invalid JSON, ignore
              }
            }}
            rows={10}
            placeholder='[{"method": "POST", "url": "/api/login"}]'
          />
        </div>
      )
    }

    return (
      <div>
        <Title level={5}>接口定义</Title>
        {data.api_definitions.length > 0 ? (
          <ul style={{ paddingLeft: 20 }}>
            {data.api_definitions.map((api, index) => (
              <li key={index} style={{ marginBottom: 8 }}>
                <Tag color="green">{api.method}</Tag>
                <code>{api.url}</code>
              </li>
            ))}
          </ul>
        ) : (
          <Paragraph type="secondary">暂无数据</Paragraph>
        )}
      </div>
    )
  }

  return (
    <Card
      title="需求分析结果"
      bordered={false}
      extra={
        <Space>
          {editing ? (
            <>
              <Button icon={<SaveOutlined />} type="primary" onClick={handleSave}>
                保存
              </Button>
              <Button icon={<CloseOutlined />} onClick={handleCancel}>
                取消
              </Button>
            </>
          ) : (
            <>
              <Button icon={<EditOutlined />} onClick={handleEdit} disabled={loading}>
                编辑
              </Button>
              <Button icon={<ReloadOutlined />} onClick={onReanalyze} loading={loading}>
                重新分析
              </Button>
            </>
          )}
        </Space>
      }
    >
      <Collapse defaultActiveKey={['1', '2', '3', '4', '5', '6']} ghost>
        <Panel header="功能点" key="1">
          {renderStringList(data.function_points, 'function_points', '功能点')}
        </Panel>

        <Panel header="业务规则" key="2">
          {renderStringList(data.business_rules, 'business_rules', '业务规则')}
        </Panel>

        <Panel header="数据模型" key="3">
          {renderDataModels()}
        </Panel>

        <Panel header="接口定义" key="4">
          {renderApiDefinitions()}
        </Panel>

        <Panel header="测试重点" key="5">
          {renderStringList(data.test_focus, 'test_focus', '测试重点')}
        </Panel>

        <Panel header="风险点" key="6">
          {renderStringList(data.risk_points, 'risk_points', '风险点')}
        </Panel>
      </Collapse>
    </Card>
  )
}

export default RequirementAnalysisResult
