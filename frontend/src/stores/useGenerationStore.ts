/**
 * Generation Process State Store
 */
import { create } from 'zustand'
import { RequirementAnalysis, Scenario, TestCase, QualityReport, CodeFiles } from '@/types'

interface GenerationState {
  // Session
  sessionId: string | null
  setSessionId: (id: string) => void

  // Current step
  currentStep: number
  setCurrentStep: (step: number) => void

  // Requirement Analysis
  requirementAnalysis: RequirementAnalysis | null
  setRequirementAnalysis: (data: RequirementAnalysis) => void

  // Scenarios
  scenarios: Scenario[]
  setScenarios: (data: Scenario[]) => void
  selectedScenarios: string[]
  setSelectedScenarios: (ids: string[]) => void

  // Test Cases
  testCases: TestCase[]
  setTestCases: (data: TestCase[]) => void
  selectedCases: string[]
  setSelectedCases: (ids: string[]) => void

  // Code
  codeFiles: CodeFiles | null
  setCodeFiles: (data: CodeFiles) => void

  // Quality Report
  qualityReport: QualityReport | null
  setQualityReport: (data: QualityReport) => void

  // Loading states
  isLoading: boolean
  setIsLoading: (loading: boolean) => void

  // Reset
  reset: () => void
}

const initialState = {
  sessionId: null,
  currentStep: 0,
  requirementAnalysis: null,
  scenarios: [],
  selectedScenarios: [],
  testCases: [],
  selectedCases: [],
  codeFiles: null,
  qualityReport: null,
  isLoading: false,
}

export const useGenerationStore = create<GenerationState>((set) => ({
  ...initialState,

  setSessionId: (id) => set({ sessionId: id }),
  setCurrentStep: (step) => set({ currentStep: step }),
  setRequirementAnalysis: (data) => set({ requirementAnalysis: data }),
  setScenarios: (data) => set({ scenarios: data }),
  setSelectedScenarios: (ids) => set({ selectedScenarios: ids }),
  setTestCases: (data) => set({ testCases: data }),
  setSelectedCases: (ids) => set({ selectedCases: ids }),
  setCodeFiles: (data) => set({ codeFiles: data }),
  setQualityReport: (data) => set({ qualityReport: data }),
  setIsLoading: (loading) => set({ isLoading: loading }),

  reset: () => set(initialState),
}))

export default useGenerationStore
