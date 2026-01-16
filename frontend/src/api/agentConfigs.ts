/**
 * Agent Configs API Services
 */
import apiClient from './client'

export type AgentType = 'requirement' | 'scenario' | 'case' | 'code' | 'quality'

export interface AgentConfig {
  id: number
  agent_type: AgentType
  agent_name: string
  model_provider: string
  model_name: string
  prompt_template: string
  model_params: Record<string, any>
  knowledge_bases: number[]
  scripts: number[]
  is_default: boolean
}

export interface UpdateAgentConfigRequest {
  model_provider?: string
  model_name?: string
  prompt_template?: string
  model_params?: Record<string, any>
  knowledge_bases?: number[]
  scripts?: number[]
}

export const agentConfigsApi = {
  // 获取所有Agent配置列表
  getList: () => {
    return apiClient.get<AgentConfig[]>('/v1/agent-configs')
  },

  // 获取指定Agent配置
  getConfig: (agentType: AgentType) => {
    return apiClient.get<AgentConfig>(`/v1/agent-configs/${agentType}`)
  },

  // 更新Agent配置
  updateConfig: (agentType: AgentType, data: UpdateAgentConfigRequest) => {
    return apiClient.put<AgentConfig>(`/v1/agent-configs/${agentType}`, data)
  },

  // 恢复默认配置
  resetConfig: (agentType: AgentType) => {
    return apiClient.post<AgentConfig>(`/v1/agent-configs/${agentType}/reset`)
  },
}

export default agentConfigsApi
