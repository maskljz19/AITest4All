/**
 * Common Type Definitions
 */

export type TestType = 'ui' | 'api' | 'unit'

export interface RequirementAnalysis {
  function_points: string[]
  business_rules: string[]
  data_models: Array<{
    entity: string
    fields: string[]
  }>
  api_definitions: Array<{
    method: string
    url: string
  }>
  test_focus: string[]
  risk_points: string[]
}

export interface Scenario {
  scenario_id: string
  name: string
  description: string
  precondition: string
  expected_result: string
  priority: string
  category: string
}

export interface TestCase {
  case_id: string
  title: string
  test_type: TestType
  priority: string
  precondition: string
  steps: Array<{
    step_no: number
    action: string
    data: string | Record<string, any>  // Support both string and object
    expected: string
  }>
  test_data: Record<string, any>
  expected_result: string
  postcondition: string
}

export interface QualityReport {
  coverage_analysis: {
    coverage_rate: number
    uncovered_points: string[]
    missing_scenarios: string[]
  }
  quality_analysis: {
    duplicate_cases: string[]
    non_smart_cases: string[]
    incomplete_data: string[]
  }
  suggestions: string[]
  quality_score: {
    coverage_score: number
    quality_score: number
    total_score: number
  }
}

export interface CodeFiles {
  files: Record<string, string>
}

export interface KnowledgeBase {
  id: number
  name: string
  type: 'case' | 'defect' | 'rule' | 'api'
  storage_type: 'local' | 'url' | 'database'
  file_path?: string
  url?: string
  content?: string
  metadata?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface PythonScript {
  id: number
  name: string
  description?: string
  code: string
  dependencies: string[]
  is_builtin: boolean
  created_at: string
  updated_at: string
}

export interface CaseTemplate {
  id: number
  name: string
  test_type: TestType
  template_structure: Record<string, any>
  is_builtin: boolean
  created_at: string
  updated_at: string
}

export interface AgentConfig {
  id: number
  agent_type: 'requirement' | 'scenario' | 'case' | 'code' | 'quality'
  agent_name: string
  model_provider: string
  model_name: string
  prompt_template: string
  model_params: Record<string, any>
  knowledge_bases: number[]
  scripts: number[]
  is_default: boolean
  created_at: string
  updated_at: string
}
