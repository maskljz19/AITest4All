"""Generation API Schemas"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum


class TestType(str, Enum):
    """Test type enumeration"""
    UI = "ui"
    API = "api"
    UNIT = "unit"


class RequirementAnalysisRequest(BaseModel):
    """Request model for requirement analysis"""
    session_id: Optional[str] = Field(None, description="Session ID for continuing a session")
    requirement_text: Optional[str] = Field(None, description="Requirement text input")
    url: Optional[str] = Field(None, description="URL to fetch requirement from")
    test_type: TestType = Field(..., description="Type of test (ui/api/unit)")
    knowledge_base_ids: Optional[List[int]] = Field(None, description="Knowledge base IDs to use")


class RequirementAnalysisResponse(BaseModel):
    """Response model for requirement analysis"""
    session_id: str = Field(..., description="Session ID")
    function_points: List[str] = Field(..., description="List of function points")
    business_rules: List[str] = Field(..., description="List of business rules")
    data_models: List[Dict[str, Any]] = Field(..., description="Data models")
    api_definitions: List[Dict[str, Any]] = Field(..., description="API definitions")
    test_focus: List[str] = Field(..., description="Test focus areas")
    risk_points: List[str] = Field(..., description="Risk points")


class ScenarioGenerationRequest(BaseModel):
    """Request model for scenario generation"""
    session_id: str = Field(..., description="Session ID")
    requirement_analysis: Dict[str, Any] = Field(..., description="Requirement analysis result")
    test_type: TestType = Field(..., description="Type of test")
    defect_kb_ids: Optional[List[int]] = Field(None, description="Defect knowledge base IDs")


class Scenario(BaseModel):
    """Scenario model"""
    scenario_id: str = Field(..., description="Scenario ID")
    name: str = Field(..., description="Scenario name")
    description: str = Field(..., description="Scenario description")
    precondition: str = Field(..., description="Precondition")
    expected_result: str = Field(..., description="Expected result")
    priority: str = Field(..., description="Priority (P0/P1/P2/P3)")
    category: str = Field(..., description="Category (normal/exception/boundary/performance/security)")


class ScenarioGenerationResponse(BaseModel):
    """Response model for scenario generation"""
    session_id: str = Field(..., description="Session ID")
    scenarios: List[Scenario] = Field(..., description="List of scenarios")


class TestStep(BaseModel):
    """Test step model"""
    step_no: int = Field(..., description="Step number")
    action: str = Field(..., description="Action to perform")
    data: Union[str, Dict[str, Any], None] = Field(default="", description="Test data (string, dict, or empty)")
    expected: str = Field(..., description="Expected result")


class TestCase(BaseModel):
    """Test case model"""
    case_id: str = Field(..., description="Test case ID")
    title: str = Field(..., description="Test case title")
    test_type: str = Field(..., description="Test type")
    priority: str = Field(..., description="Priority")
    precondition: str = Field(..., description="Precondition")
    steps: List[TestStep] = Field(..., description="Test steps")
    test_data: Dict[str, Any] = Field(..., description="Test data")
    expected_result: str = Field(..., description="Expected result")
    postcondition: str = Field(..., description="Postcondition")


class CaseGenerationRequest(BaseModel):
    """Request model for case generation"""
    session_id: str = Field(..., description="Session ID")
    scenarios: List[Scenario] = Field(..., description="List of scenarios")
    template_id: Optional[int] = Field(None, description="Template ID")
    script_ids: Optional[List[int]] = Field(None, description="Script IDs to use")


class CaseGenerationResponse(BaseModel):
    """Response model for case generation"""
    session_id: str = Field(..., description="Session ID")
    test_cases: List[TestCase] = Field(..., description="List of test cases")


class CodeGenerationRequest(BaseModel):
    """Request model for code generation"""
    session_id: str = Field(..., description="Session ID")
    test_cases: List[TestCase] = Field(..., description="List of test cases")
    tech_stack: Optional[str] = Field(None, description="Custom tech stack description")
    use_default_stack: bool = Field(True, description="Use default tech stack")


class CodeGenerationResponse(BaseModel):
    """Response model for code generation"""
    session_id: str = Field(..., description="Session ID")
    files: Dict[str, str] = Field(..., description="Generated code files")


class QualityAnalysisRequest(BaseModel):
    """Request model for quality analysis"""
    session_id: str = Field(..., description="Session ID")
    requirement_analysis: Dict[str, Any] = Field(..., description="Requirement analysis result")
    scenarios: List[Scenario] = Field(..., description="List of scenarios")
    test_cases: List[TestCase] = Field(..., description="List of test cases")
    defect_kb_ids: Optional[List[int]] = Field(None, description="Defect knowledge base IDs")


class CoverageAnalysis(BaseModel):
    """Coverage analysis model"""
    coverage_rate: float = Field(..., description="Coverage rate percentage")
    uncovered_points: List[str] = Field(..., description="Uncovered points")
    missing_scenarios: List[str] = Field(..., description="Missing scenarios")


class QualityAnalysis(BaseModel):
    """Quality analysis model"""
    duplicate_cases: List[str] = Field(..., description="Duplicate cases")
    non_smart_cases: List[str] = Field(..., description="Non-SMART cases")
    incomplete_data: List[str] = Field(..., description="Incomplete data")


class QualityScore(BaseModel):
    """Quality score model"""
    coverage_score: float = Field(..., description="Coverage score")
    quality_score: float = Field(..., description="Quality score")
    total_score: float = Field(..., description="Total score")


class QualityAnalysisResponse(BaseModel):
    """Response model for quality analysis"""
    session_id: str = Field(..., description="Session ID")
    coverage_analysis: CoverageAnalysis = Field(..., description="Coverage analysis")
    quality_analysis: QualityAnalysis = Field(..., description="Quality analysis")
    suggestions: List[str] = Field(..., description="Improvement suggestions")
    quality_score: QualityScore = Field(..., description="Quality score")


class OptimizeRequest(BaseModel):
    """Request model for case optimization"""
    session_id: str = Field(..., description="Session ID")
    selected_cases: List[TestCase] = Field(..., description="Selected test cases")
    instruction: str = Field(..., description="Optimization instruction")


class OptimizeResponse(BaseModel):
    """Response model for case optimization"""
    session_id: str = Field(..., description="Session ID")
    optimized_cases: List[TestCase] = Field(..., description="Optimized test cases")


class SupplementRequest(BaseModel):
    """Request model for case supplement"""
    session_id: str = Field(..., description="Session ID")
    existing_cases: List[TestCase] = Field(..., description="Existing test cases")
    requirement: str = Field(..., description="Requirement description")


class SupplementResponse(BaseModel):
    """Response model for case supplement"""
    session_id: str = Field(..., description="Session ID")
    new_cases: List[TestCase] = Field(..., description="New test cases")


class ErrorResponse(BaseModel):
    """Error response model"""
    error_code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Any] = Field(None, description="Error details")
    retry_after: Optional[int] = Field(None, description="Retry after seconds")
