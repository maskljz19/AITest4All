/**
 * Knowledge Base API Services
 */
import apiClient from './client'

export interface UploadDocumentRequest {
  file: File
  name: string
  type: 'case' | 'defect' | 'rule' | 'api'
  project?: string
}

export interface AddUrlRequest {
  url: string
  name: string
  type: 'case' | 'defect' | 'rule' | 'api'
  project?: string
}

export interface SearchRequest {
  query: string
  type?: string
  project?: string
  limit?: number
}

export const knowledgeBaseApi = {
  // 上传文档
  uploadDocument: (data: UploadDocumentRequest) => {
    const formData = new FormData()
    formData.append('file', data.file)
    formData.append('name', data.name)
    formData.append('type', data.type)
    if (data.project) {
      formData.append('project', data.project)
    }

    return apiClient.post('/v1/knowledge-base/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 添加外链
  addUrl: (data: AddUrlRequest) => {
    return apiClient.post('/v1/knowledge-base/url', data)
  },

  // 获取列表
  getList: (params?: { type?: string; project?: string; page?: number; page_size?: number }) => {
    return apiClient.get('/v1/knowledge-base/list', { params })
  },

  // 获取详情
  getDetail: (id: number) => {
    return apiClient.get(`/v1/knowledge-base/${id}`)
  },

  // 删除文档
  deleteDocument: (id: number) => {
    return apiClient.delete(`/v1/knowledge-base/${id}`)
  },

  // 搜索
  search: (params: SearchRequest) => {
    return apiClient.get('/v1/knowledge-base/search', { params })
  },
}

export default knowledgeBaseApi
