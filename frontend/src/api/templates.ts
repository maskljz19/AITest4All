/**
 * Templates API Services
 */
import apiClient from './client'

export interface CreateTemplateRequest {
  name: string
  test_type: 'ui' | 'api' | 'unit'
  template_structure: Record<string, any>
}

export interface UpdateTemplateRequest {
  name?: string
  test_type?: 'ui' | 'api' | 'unit'
  template_structure?: Record<string, any>
}

export const templatesApi = {
  // 创建模板
  create: (data: CreateTemplateRequest) => {
    return apiClient.post('/v1/templates', data)
  },

  // 获取列表
  getList: (params?: { test_type?: string; page?: number; page_size?: number }) => {
    return apiClient.get('/v1/templates', { params })
  },

  // 获取详情
  getDetail: (id: number) => {
    return apiClient.get(`/v1/templates/${id}`)
  },

  // 更新模板
  update: (id: number, data: UpdateTemplateRequest) => {
    return apiClient.put(`/v1/templates/${id}`, data)
  },

  // 删除模板
  delete: (id: number) => {
    return apiClient.delete(`/v1/templates/${id}`)
  },
}

export default templatesApi
