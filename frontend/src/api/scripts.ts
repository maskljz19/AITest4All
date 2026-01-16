/**
 * Scripts API Services
 */
import apiClient from './client'

export interface CreateScriptRequest {
  name: string
  description?: string
  code: string
  dependencies?: string[]
}

export interface UpdateScriptRequest {
  name?: string
  description?: string
  code?: string
  dependencies?: string[]
}

export interface TestScriptRequest {
  args?: Record<string, any>
}

export const scriptsApi = {
  // 创建脚本
  create: (data: CreateScriptRequest) => {
    return apiClient.post('/v1/scripts', data)
  },

  // 获取列表
  getList: (params?: { page?: number; page_size?: number }) => {
    return apiClient.get('/v1/scripts', { params })
  },

  // 获取详情
  getDetail: (id: number) => {
    return apiClient.get(`/v1/scripts/${id}`)
  },

  // 更新脚本
  update: (id: number, data: UpdateScriptRequest) => {
    return apiClient.put(`/v1/scripts/${id}`, data)
  },

  // 删除脚本
  delete: (id: number) => {
    return apiClient.delete(`/v1/scripts/${id}`)
  },

  // 测试执行
  test: (id: number, data?: TestScriptRequest) => {
    return apiClient.post(`/v1/scripts/${id}/test`, data)
  },
}

export default scriptsApi
