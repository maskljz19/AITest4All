/**
 * Export API Services
 */
import apiClient from './client'

export interface ExportCasesRequest {
  session_id: string
  format: 'excel' | 'word' | 'json' | 'markdown' | 'html'
  include_requirement?: boolean
  include_scenarios?: boolean
  include_cases?: boolean
  include_quality_report?: boolean
}

export interface ExportCodeRequest {
  session_id: string
  format: 'zip' | 'single' | 'project'
}

export const exportApi = {
  // 导出用例
  exportCases: (data: ExportCasesRequest) => {
    return apiClient.post('/v1/export/cases', data, {
      responseType: 'blob',
    })
  },

  // 导出代码
  exportCode: (data: ExportCodeRequest) => {
    return apiClient.post('/v1/export/code', data, {
      responseType: 'blob',
    })
  },
}

export default exportApi
