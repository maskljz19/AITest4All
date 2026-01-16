import React, { useState, useEffect } from 'react'
import {
  Card,
  Button,
  Form,
  Input,
  Select,
  InputNumber,
  message,
  Space,
  Tabs,
  Divider,
  Tag,
  Alert,
  Popconfirm,
  Spin,
  Modal,
} from 'antd'
import {
  SaveOutlined,
  ReloadOutlined,
  UndoOutlined,
} from '@ant-design/icons'
import Editor from '@monaco-editor/react'
import { agentConfigsApi, type AgentType, type AgentConfig } from '../api/agentConfigs'
import { knowledgeBaseApi } from '../api/knowledgeBase'
import { scriptsApi } from '../api/scripts'

const { TabPane } = Tabs

interface KnowledgeBase {
  id: number
  name: string
  type: string
}

interface Script {
  id: number
  name: string
}

const SettingsPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [activeAgent, setActiveAgent] = useState<AgentType>('requirement')
  const [agentConfigs, setAgentConfigs] = useState<Record<AgentType, AgentConfig | null>>({
    requirement: null,
    scenario: null,
    case: null,
    code: null,
    quality: null,
  })
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [scripts, setScripts] = useState<Script[]>([])
  const [hasChanges, setHasChanges] = useState(false)

  const [form] = Form.useForm()

  // Agent类型映射
  const agentTypeMap: Record<AgentType, string> = {
    requirement: '需求分析Agent',
    scenario: '场景生成Agent',
    case: '用例生成Agent',
    code: '代码生成Agent',
    quality: '质量优化Agent',
  }

  // 加载所有配置
  const loadAllConfigs = async () => {
    setLoading(true)
    try {
      const [configsRes, kbRes, scriptsRes] = await Promise.all([
        agentConfigsApi.getList(),
        knowledgeBaseApi.getList(),
        scriptsApi.getList(),
      ])

      const configsMap: Record<AgentType, AgentConfig | null> = {
        requirement: null,
        scenario: null,
        case: null,
        code: null,
        quality: null,
      }

      configsRes.data.forEach((config: AgentConfig) => {
        configsMap[config.agent_type] = config
      })

      setAgentConfigs(configsMap)
      setKnowledgeBases(kbRes.data || [])
      setScripts(scriptsRes.data || [])

      // 加载当前Agent配置到表单
      if (configsMap[activeAgent]) {
        loadConfigToForm(configsMap[activeAgent]!)
      }
    } catch (error: any) {
      message.error(error.response?.data?.message || '加载配置失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadAllConfigs()
  }, [])

  // 加载配置到表单
  const loadConfigToForm = (config: AgentConfig) => {
    form.setFieldsValue({
      model_provider: config.model_provider,
      model_name: config.model_name,
      prompt_template: config.prompt_template,
      temperature: config.model_params?.temperature || 0.7,
      max_tokens: config.model_params?.max_tokens || 2000,
      top_p: config.model_params?.top_p || 1.0,
      knowledge_bases: config.knowledge_bases || [],
      scripts: config.scripts || [],
    })
    setHasChanges(false)
  }

  // 切换Agent
  const handleAgentChange = (agentType: AgentType) => {
    if (hasChanges) {
      Modal.confirm({
        title: '有未保存的更改',
        content: '切换Agent将丢失当前未保存的更改，是否继续？',
        onOk: () => {
          setActiveAgent(agentType)
          const config = agentConfigs[agentType]
          if (config) {
            loadConfigToForm(config)
          }
        },
      })
    } else {
      setActiveAgent(agentType)
      const config = agentConfigs[agentType]
      if (config) {
        loadConfigToForm(config)
      }
    }
  }

  // 保存配置
  const handleSave = async (values: any) => {
    setSaving(true)
    try {
      const data = {
        model_provider: values.model_provider,
        model_name: values.model_name,
        prompt_template: values.prompt_template,
        model_params: {
          temperature: values.temperature,
          max_tokens: values.max_tokens,
          top_p: values.top_p,
        },
        knowledge_bases: values.knowledge_bases || [],
        scripts: values.scripts || [],
      }

      const response = await agentConfigsApi.updateConfig(activeAgent, data)
      
      // 更新本地状态
      setAgentConfigs({
        ...agentConfigs,
        [activeAgent]: response.data,
      })

      message.success('保存成功')
      setHasChanges(false)
    } catch (error: any) {
      message.error(error.response?.data?.message || '保存失败')
    } finally {
      setSaving(false)
    }
  }

  // 恢复默认配置
  const handleReset = async () => {
    setLoading(true)
    try {
      const response = await agentConfigsApi.resetConfig(activeAgent)
      
      // 更新本地状态
      setAgentConfigs({
        ...agentConfigs,
        [activeAgent]: response.data,
      })

      // 重新加载到表单
      loadConfigToForm(response.data)
      message.success('已恢复默认配置')
    } catch (error: any) {
      message.error(error.response?.data?.message || '恢复默认配置失败')
    } finally {
      setLoading(false)
    }
  }

  // 表单值变化
  const handleFormChange = () => {
    setHasChanges(true)
  }

  const currentConfig = agentConfigs[activeAgent]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Agent配置</h1>

      <Card>
        <Alert
          message="配置说明"
          description="在这里可以配置每个Agent的AI模型、提示词模板、参数以及关联的知识库和脚本。修改后请点击保存按钮。"
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Tabs
          activeKey={activeAgent}
          onChange={(key) => handleAgentChange(key as AgentType)}
          tabPosition="left"
          style={{ minHeight: 600 }}
        >
          {Object.entries(agentTypeMap).map(([type, name]) => (
            <TabPane
              tab={
                <Space>
                  {name}
                  {agentConfigs[type as AgentType]?.is_default && (
                    <Tag color="green">默认</Tag>
                  )}
                </Space>
              }
              key={type}
            >
              <Spin spinning={loading}>
                {currentConfig && (
                  <Form
                    form={form}
                    layout="vertical"
                    onFinish={handleSave}
                    onValuesChange={handleFormChange}
                  >
                    <Divider orientation="left">模型配置</Divider>

                    <Form.Item
                      name="model_provider"
                      label="模型提供商"
                      rules={[{ required: true, message: '请选择模型提供商' }]}
                    >
                      <Select
                        placeholder="请选择模型提供商"
                        options={[
                          { label: 'OpenAI', value: 'openai' },
                          { label: 'Anthropic', value: 'anthropic' },
                          { label: '本地模型', value: 'local' },
                          { label: '其他API', value: 'other' },
                        ]}
                      />
                    </Form.Item>

                    <Form.Item
                      name="model_name"
                      label="模型名称"
                      rules={[{ required: true, message: '请输入模型名称' }]}
                    >
                      <Input placeholder="例如: gpt-4, claude-3-opus" />
                    </Form.Item>

                    <Divider orientation="left">模型参数</Divider>

                    <Form.Item
                      name="temperature"
                      label="Temperature"
                      tooltip="控制输出的随机性，范围0-2，值越大越随机"
                      rules={[{ required: true, message: '请输入Temperature' }]}
                    >
                      <InputNumber
                        min={0}
                        max={2}
                        step={0.1}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>

                    <Form.Item
                      name="max_tokens"
                      label="Max Tokens"
                      tooltip="最大输出token数量"
                      rules={[{ required: true, message: '请输入Max Tokens' }]}
                    >
                      <InputNumber min={100} max={8000} style={{ width: '100%' }} />
                    </Form.Item>

                    <Form.Item
                      name="top_p"
                      label="Top P"
                      tooltip="核采样参数，范围0-1"
                      rules={[{ required: true, message: '请输入Top P' }]}
                    >
                      <InputNumber
                        min={0}
                        max={1}
                        step={0.1}
                        style={{ width: '100%' }}
                      />
                    </Form.Item>

                    <Divider orientation="left">提示词模板</Divider>

                    <Form.Item
                      name="prompt_template"
                      label="提示词"
                      rules={[{ required: true, message: '请输入提示词模板' }]}
                    >
                      <Editor
                        height="300px"
                        defaultLanguage="markdown"
                        theme="vs-dark"
                        options={{
                          minimap: { enabled: false },
                          fontSize: 14,
                          lineNumbers: 'on',
                          scrollBeyondLastLine: false,
                          automaticLayout: true,
                          wordWrap: 'on',
                        }}
                        onChange={(value) =>
                          form.setFieldValue('prompt_template', value)
                        }
                      />
                    </Form.Item>

                    <Divider orientation="left">关联资源</Divider>

                    <Form.Item
                      name="knowledge_bases"
                      label="关联知识库"
                      tooltip="选择此Agent可以使用的知识库"
                    >
                      <Select
                        mode="multiple"
                        placeholder="请选择知识库"
                        options={knowledgeBases.map((kb) => ({
                          label: `${kb.name} (${kb.type})`,
                          value: kb.id,
                        }))}
                        showSearch
                        filterOption={(input, option) =>
                          (option?.label ?? '')
                            .toLowerCase()
                            .includes(input.toLowerCase())
                        }
                      />
                    </Form.Item>

                    <Form.Item
                      name="scripts"
                      label="关联脚本"
                      tooltip="选择此Agent可以调用的脚本"
                    >
                      <Select
                        mode="multiple"
                        placeholder="请选择脚本"
                        options={scripts.map((script) => ({
                          label: script.name,
                          value: script.id,
                        }))}
                        showSearch
                        filterOption={(input, option) =>
                          (option?.label ?? '')
                            .toLowerCase()
                            .includes(input.toLowerCase())
                        }
                      />
                    </Form.Item>

                    <Divider />

                    <Form.Item>
                      <Space>
                        <Button
                          type="primary"
                          icon={<SaveOutlined />}
                          htmlType="submit"
                          loading={saving}
                          disabled={!hasChanges}
                        >
                          保存配置
                        </Button>
                        <Popconfirm
                          title="确定恢复默认配置吗？"
                          description="此操作将覆盖当前配置"
                          onConfirm={handleReset}
                          okText="确定"
                          cancelText="取消"
                        >
                          <Button icon={<UndoOutlined />} disabled={loading}>
                            恢复默认
                          </Button>
                        </Popconfirm>
                        <Button
                          icon={<ReloadOutlined />}
                          onClick={() => {
                            if (currentConfig) {
                              loadConfigToForm(currentConfig)
                            }
                          }}
                          disabled={!hasChanges}
                        >
                          撤销更改
                        </Button>
                      </Space>
                    </Form.Item>
                  </Form>
                )}
              </Spin>
            </TabPane>
          ))}
        </Tabs>
      </Card>
    </div>
  )
}

export default SettingsPage
