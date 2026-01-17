/**
 * Generate Page - Test Case Generation Wizard
 * 用例生成向导页面 - 完整的测试用例生成流程
 */
import React, { useState, useEffect } from 'react'
import { Steps, Button, Space, message } from 'antd'
import { useGenerationStore } from '@/stores/useGenerationStore'
import { knowledgeBaseApi } from '@/api/knowledgeBase'
import { generateApi } from '@/api/generate'
import {
  RequirementInput,
  RequirementAnalysisResult,
  ScenarioList,
  TestCaseList,
  CodeGeneration,
  QualityReport,
  ExportPanel,
} from '@/components/Generate'
import type { RequirementInputData } from '@/components/Generate/RequirementInput'

const { Step } = Steps

const Generate: React.FC = () => {
  const {
    sessionId,
    setSessionId,
    currentStep,
    setCurrentStep,
    requirementAnalysis,
    setRequirementAnalysis,
    scenarios,
    setScenarios,
    selectedScenarios,
    setSelectedScenarios,
    testCases,
    setTestCases,
    selectedCases,
    setSelectedCases,
    codeFiles,
    setCodeFiles,
    qualityReport,
    setQualityReport,
    isLoading,
    setIsLoading,
    reset,
  } = useGenerationStore()

  const [knowledgeBases, setKnowledgeBases] = useState<any[]>([])

  useEffect(() => {
    // Load knowledge bases
    loadKnowledgeBases()
  }, [])

  const loadKnowledgeBases = async () => {
    try {
      const response = await knowledgeBaseApi.getList()
      // Backend returns { success: true, data: [...], total: ... }
      setKnowledgeBases(Array.isArray(response.data.data) ? response.data.data : [])
    } catch (error) {
      console.error('Failed to load knowledge bases:', error)
      setKnowledgeBases([])
    }
  }

  const handleRequirementSubmit = async (data: RequirementInputData) => {
    setIsLoading(true)
    try {
      const response = await generateApi.analyzeRequirement({
        requirement_text: data.text,
        file: data.file,
        url: data.url,
        test_type: data.testType,
        knowledge_base_ids: data.knowledgeBaseIds,
        session_id: sessionId || undefined,
      })

      // Backend returns flat structure with session_id and analysis fields
      const { session_id, ...analysisResult } = response.data
      
      setSessionId(session_id)
      setRequirementAnalysis(analysisResult)
      setCurrentStep(1)
      message.success('需求分析完成')
    } catch (error: any) {
      message.error(error.response?.data?.message || '需求分析失败')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReanalyze = async () => {
    if (!requirementAnalysis) return
    setCurrentStep(0)
  }

  const handleRequirementUpdate = (data: any) => {
    setRequirementAnalysis(data)
  }

  const handleGenerateScenarios = async () => {
    if (!requirementAnalysis || !sessionId) {
      message.warning('缺少必要数据，请先完成需求分析')
      return
    }

    setIsLoading(true)
    try {
      const response = await generateApi.generateScenarios({
        session_id: sessionId,
        requirement_analysis: requirementAnalysis,
        test_type: 'ui',
      })

      setScenarios(response.data.scenarios)
      setSelectedScenarios(response.data.scenarios.map((s: any) => s.scenario_id))
      setCurrentStep(2)
      message.success('场景生成完成')
    } catch (error: any) {
      message.error(error.response?.data?.message || '场景生成失败')
    } finally {
      setIsLoading(false)
    }
  }

  const handleScenarioDelete = (id: string) => {
    setScenarios(scenarios.filter((s) => s.scenario_id !== id))
    setSelectedScenarios(selectedScenarios.filter((sid) => sid !== id))
  }

  const handleScenarioSupplement = async (_instruction: string) => {
    // TODO: Implement scenario supplement
    message.info('场景补充功能开发中')
  }

  const handleGenerateCases = async () => {
    if (!sessionId || selectedScenarios.length === 0) return

    setIsLoading(true)
    try {
      const selectedScenarioData = scenarios.filter((s) =>
        selectedScenarios.includes(s.scenario_id)
      )

      const response = await generateApi.generateCases({
        session_id: sessionId,
        scenarios: selectedScenarioData,
      })

      setTestCases(response.data.test_cases)
      setSelectedCases(response.data.test_cases.map((c: any) => c.case_id))
      setCurrentStep(3)
      message.success('用例生成完成')
    } catch (error: any) {
      message.error(error.response?.data?.message || '用例生成失败')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCaseUpdate = (caseId: string, data: any) => {
    setTestCases(testCases.map((c) => (c.case_id === caseId ? data : c)))
  }

  const handleCaseOptimize = async (selectedIds: string[], instruction: string) => {
    if (!sessionId) return

    setIsLoading(true)
    try {
      const selectedCaseData = testCases.filter((c) => selectedIds.includes(c.case_id))

      const response = await generateApi.optimizeCases({
        session_id: sessionId,
        selected_cases: selectedCaseData,
        instruction,
      })

      // Update optimized cases
      const optimizedCases = response.data.optimized_cases
      setTestCases(
        testCases.map((c) => {
          const optimized = optimizedCases.find((oc: any) => oc.case_id === c.case_id)
          return optimized || c
        })
      )
      message.success('用例优化完成')
    } catch (error: any) {
      message.error(error.response?.data?.message || '用例优化失败')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateCode = async (useDefaultStack: boolean, techStack?: string) => {
    if (!sessionId || testCases.length === 0) return

    setIsLoading(true)
    try {
      const response = await generateApi.generateCode({
        session_id: sessionId,
        test_cases: testCases,
        use_default_stack: useDefaultStack,
        tech_stack: techStack,
      })

      // Backend returns { session_id, files: {...} }
      // Wrap it in the expected structure for the component
      const codeData = response.data.files ? { files: response.data.files } : response.data
      setCodeFiles(codeData)
      setCurrentStep(4)
      message.success('代码生成完成')
    } catch (error: any) {
      message.error(error.response?.data?.message || '代码生成失败')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCodeUpdate = (files: any) => {
    // Ensure the structure is correct
    if (files && files.files) {
      setCodeFiles(files)
    } else if (files) {
      setCodeFiles({ files })
    }
  }

  const handleAnalyzeQuality = async () => {
    if (!sessionId || !requirementAnalysis || testCases.length === 0) return

    setIsLoading(true)
    try {
      const response = await generateApi.analyzeQuality({
        session_id: sessionId,
        requirement_analysis: requirementAnalysis,
        scenarios,
        test_cases: testCases,
      })

      setQualityReport(response.data)
      setCurrentStep(5)
      message.success('质量分析完成')
    } catch (error: any) {
      message.error(error.response?.data?.message || '质量分析失败')
    } finally {
      setIsLoading(false)
    }
  }

  const handleNext = () => {
    if (currentStep === 1) {
      handleGenerateScenarios()
    } else if (currentStep === 2) {
      handleGenerateCases()
    } else if (currentStep === 3) {
      handleAnalyzeQuality()
    } else {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrev = () => {
    setCurrentStep(currentStep - 1)
  }

  const handleReset = () => {
    reset()
    message.info('已重置')
  }

  const steps = [
    { title: '需求输入', description: '上传或输入需求文档' },
    { title: '需求分析', description: '分析需求并提取关键信息' },
    { title: '场景生成', description: '生成测试场景' },
    { title: '用例生成', description: '生成详细测试用例' },
    { title: '代码生成', description: '生成自动化测试代码' },
    { title: '质量报告', description: '分析用例质量' },
    { title: '导出', description: '导出测试用例和代码' },
  ]

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>用例生成向导</h1>

      <Steps current={currentStep} style={{ marginBottom: 32 }}>
        {steps.map((step) => (
          <Step key={step.title} title={step.title} description={step.description} />
        ))}
      </Steps>

      <div style={{ marginBottom: 24 }}>
        {currentStep === 0 && (
          <RequirementInput
            onSubmit={handleRequirementSubmit}
            loading={isLoading}
            knowledgeBases={knowledgeBases}
          />
        )}

        {currentStep === 1 && requirementAnalysis && (
          <>
            <RequirementAnalysisResult
              data={requirementAnalysis}
              onUpdate={handleRequirementUpdate}
              onReanalyze={handleReanalyze}
              loading={isLoading}
            />
            <div style={{ marginTop: 24, textAlign: 'center' }}>
              <Button
                type="primary"
                size="large"
                onClick={handleGenerateScenarios}
                loading={isLoading}
              >
                生成场景
              </Button>
            </div>
          </>
        )}

        {currentStep === 2 && (
          <>
            <ScenarioList
              scenarios={scenarios}
              selectedIds={selectedScenarios}
              onSelectionChange={setSelectedScenarios}
              onDelete={handleScenarioDelete}
              onSupplement={handleScenarioSupplement}
              loading={isLoading}
            />
            <div style={{ marginTop: 24, textAlign: 'center' }}>
              <Button
                type="primary"
                size="large"
                onClick={handleGenerateCases}
                loading={isLoading}
                disabled={selectedScenarios.length === 0}
              >
                生成用例
              </Button>
            </div>
          </>
        )}

        {currentStep === 3 && (
          <>
            <TestCaseList
              testCases={testCases}
              selectedIds={selectedCases}
              onSelectionChange={setSelectedCases}
              onUpdate={handleCaseUpdate}
              onOptimize={handleCaseOptimize}
              loading={isLoading}
            />
            <div style={{ marginTop: 24, textAlign: 'center' }}>
              <Space size="large">
                <Button
                  type="default"
                  size="large"
                  onClick={handleAnalyzeQuality}
                  loading={isLoading}
                >
                  质量分析
                </Button>
                <Button
                  type="primary"
                  size="large"
                  onClick={() => handleGenerateCode(true)}
                  loading={isLoading}
                  disabled={selectedCases.length === 0}
                >
                  生成代码
                </Button>
              </Space>
            </div>
          </>
        )}

        {currentStep === 4 && (
          <CodeGeneration
            codeFiles={codeFiles}
            onGenerate={handleGenerateCode}
            onUpdate={handleCodeUpdate}
            loading={isLoading}
          />
        )}

        {currentStep === 5 && <QualityReport report={qualityReport} />}

        {currentStep === 6 && (
          <ExportPanel
            sessionId={sessionId}
            hasRequirement={!!requirementAnalysis}
            hasScenarios={scenarios.length > 0}
            hasCases={testCases.length > 0}
            hasCode={!!codeFiles}
            hasQualityReport={!!qualityReport}
          />
        )}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <Space>
          {currentStep > 0 && (
            <Button onClick={handlePrev} disabled={isLoading}>
              上一步
            </Button>
          )}
          {currentStep < 6 && currentStep > 0 && (
            <Button type="primary" onClick={handleNext} loading={isLoading}>
              {currentStep === 1 ? '生成场景' : currentStep === 2 ? '生成用例' : currentStep === 3 ? '质量分析' : '下一步'}
            </Button>
          )}
        </Space>
        <Button onClick={handleReset} disabled={isLoading}>
          重新开始
        </Button>
      </div>
    </div>
  )
}

export default Generate
