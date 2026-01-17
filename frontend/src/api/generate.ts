/**
 * Generation API Services
 */
import apiClient from './client'

export interface RequirementAnalysisRequest {
  session_id?: string
  requirement_text?: string
  file?: File
  url?: string
  test_type: 'ui' | 'api' | 'unit'
  knowledge_base_ids?: number[]
}

export interface ScenarioGenerationRequest {
  session_id: string
  requirement_analysis: any
  test_type: 'ui' | 'api' | 'unit'
  defect_kb_ids?: number[]
}

export interface CaseGenerationRequest {
  session_id: string
  scenarios: any[]
  template_id?: number
  script_ids?: number[]
}

export interface CodeGenerationRequest {
  session_id: string
  test_cases: any[]
  tech_stack?: string
  use_default_stack: boolean
}

export interface QualityAnalysisRequest {
  session_id: string
  requirement_analysis: any
  scenarios: any[]
  test_cases: any[]
  defect_kb_ids?: number[]
}

export interface OptimizeRequest {
  session_id: string
  selected_cases: any[]
  instruction: string
}

export interface SupplementRequest {
  session_id: string
  existing_cases: any[]
  requirement: string
}

export const generateApi = {
  // 需求分析
  analyzeRequirement: (data: RequirementAnalysisRequest) => {
    const formData = new FormData()
    if (data.file) {
      formData.append('file', data.file)
    }
    if (data.requirement_text) {
      formData.append('requirement_text', data.requirement_text)
    }
    if (data.url) {
      formData.append('url', data.url)
    }
    formData.append('test_type', data.test_type)
    if (data.session_id) {
      formData.append('session_id', data.session_id)
    }
    if (data.knowledge_base_ids && data.knowledge_base_ids.length > 0) {
      formData.append('knowledge_base_ids', data.knowledge_base_ids.join(','))
    }

    return apiClient.post('/v1/generate/requirement', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },

  // 场景生成
  generateScenarios: (data: ScenarioGenerationRequest) => {
    return apiClient.post('/v1/generate/scenario', data)
  },

  // 用例生成
  generateCases: (data: CaseGenerationRequest) => {
    return apiClient.post('/v1/generate/case', data)
  },

  // 代码生成
  generateCode: (data: CodeGenerationRequest) => {
    return apiClient.post('/v1/generate/code', data)
  },

  // 质量分析
  analyzeQuality: (data: QualityAnalysisRequest) => {
    return apiClient.post('/v1/generate/quality', data)
  },

  // 优化用例
  optimizeCases: (data: OptimizeRequest) => {
    return apiClient.post('/v1/optimize', data)
  },

  // 补充用例
  supplementCases: (data: SupplementRequest) => {
    return apiClient.post('/v1/supplement', data)
  },
}

export default generateApi
