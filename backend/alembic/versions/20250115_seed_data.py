"""seed initial data

Revision ID: 002
Revises: 001
Create Date: 2025-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Define table references for bulk insert
    python_scripts_table = table(
        'python_scripts',
        column('name', String),
        column('description', Text),
        column('code', Text),
        column('dependencies', ARRAY(String)),
        column('is_builtin', Boolean),
    )
    
    agent_configs_table = table(
        'agent_configs',
        column('agent_type', String),
        column('agent_name', String),
        column('model_provider', String),
        column('model_name', String),
        column('prompt_template', Text),
        column('model_params', JSONB),
        column('is_default', Boolean),
    )

    # Insert builtin Python scripts
    op.bulk_insert(
        python_scripts_table,
        [
            {
                'name': 'generate_phone_number',
                'description': '生成随机中国手机号',
                'code': '''import random

def generate_phone_number():
    """生成随机中国手机号"""
    prefix = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
              '150', '151', '152', '153', '155', '156', '157', '158', '159',
              '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
    return random.choice(prefix) + ''.join([str(random.randint(0, 9)) for _ in range(8)])

if __name__ == '__main__':
    print(generate_phone_number())
''',
                'dependencies': [],
                'is_builtin': True,
            },
            {
                'name': 'generate_email',
                'description': '生成随机邮箱地址',
                'code': '''import random
import string

def generate_email():
    """生成随机邮箱地址"""
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    domains = ['test.com', 'example.com', 'demo.com', 'mail.com']
    return f"{username}@{random.choice(domains)}"

if __name__ == '__main__':
    print(generate_email())
''',
                'dependencies': [],
                'is_builtin': True,
            },
            {
                'name': 'generate_id_card',
                'description': '生成随机身份证号(18位)',
                'code': '''import random
from datetime import datetime, timedelta

def generate_id_card():
    """生成随机身份证号(18位)"""
    # 地区码(前6位) - 使用北京市东城区
    area_code = '110101'
    
    # 出生日期(8位) - 随机生成1970-2000年之间
    start_date = datetime(1970, 1, 1)
    end_date = datetime(2000, 12, 31)
    random_days = random.randint(0, (end_date - start_date).days)
    birth_date = start_date + timedelta(days=random_days)
    birth_str = birth_date.strftime('%Y%m%d')
    
    # 顺序码(3位)
    sequence = str(random.randint(0, 999)).zfill(3)
    
    # 前17位
    id_17 = area_code + birth_str + sequence
    
    # 计算校验码
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    sum_val = sum(int(id_17[i]) * weights[i] for i in range(17))
    check_code = check_codes[sum_val % 11]
    
    return id_17 + check_code

if __name__ == '__main__':
    print(generate_id_card())
''',
                'dependencies': [],
                'is_builtin': True,
            },
            {
                'name': 'get_timestamp',
                'description': '获取当前时间戳(毫秒)',
                'code': '''import time

def get_timestamp():
    """获取当前时间戳(毫秒)"""
    return int(time.time() * 1000)

if __name__ == '__main__':
    print(get_timestamp())
''',
                'dependencies': [],
                'is_builtin': True,
            },
            {
                'name': 'md5_encrypt',
                'description': 'MD5加密',
                'code': '''import hashlib

def md5_encrypt(text):
    """MD5加密"""
    return hashlib.md5(text.encode()).hexdigest()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        print(md5_encrypt(sys.argv[1]))
    else:
        print(md5_encrypt('test123'))
''',
                'dependencies': [],
                'is_builtin': True,
            },
            {
                'name': 'generate_username',
                'description': '生成随机用户名',
                'code': '''import random
import string

def generate_username():
    """生成随机用户名"""
    prefix = random.choice(['user', 'test', 'demo', 'admin'])
    suffix = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}{suffix}"

if __name__ == '__main__':
    print(generate_username())
''',
                'dependencies': [],
                'is_builtin': True,
            },
        ]
    )

    # Insert default Agent configurations
    op.bulk_insert(
        agent_configs_table,
        [
            {
                'agent_type': 'requirement',
                'agent_name': '需求分析Agent',
                'model_provider': 'openai',
                'model_name': 'gpt-4',
                'prompt_template': '''你是一个专业的测试需求分析专家。请分析以下需求文档，提取测试关键信息。

需求文档:
{requirement_text}

{knowledge_base_context}

请按照以下JSON格式输出分析结果:
{{
  "function_points": ["功能点1", "功能点2"],
  "business_rules": ["规则1", "规则2"],
  "data_models": [{{"entity": "实体名", "fields": ["字段1", "字段2"]}}],
  "api_definitions": [{{"method": "POST", "url": "/api/xxx", "description": "描述"}}],
  "test_focus": ["测试重点1", "测试重点2"],
  "risk_points": ["风险点1", "风险点2"]
}}

注意:
1. 功能点要具体明确
2. 业务规则要完整准确
3. 数据模型要包含关键字段
4. API定义要包含方法、路径和描述
5. 测试重点要突出核心功能
6. 风险点要识别潜在问题
''',
                'model_params': {'temperature': 0.3, 'max_tokens': 2000},
                'is_default': True,
            },
            {
                'agent_type': 'scenario',
                'agent_name': '场景生成Agent',
                'model_provider': 'openai',
                'model_name': 'gpt-4',
                'prompt_template': '''你是一个专业的测试场景设计专家。请根据需求分析结果，生成全面的测试场景。

需求分析结果:
{requirement_analysis}

测试类型: {test_type}

{defect_history}

请按照以下JSON格式输出场景列表:
[
  {{
    "scenario_id": "S001",
    "name": "场景名称",
    "description": "场景描述",
    "precondition": "前置条件",
    "expected_result": "预期结果",
    "priority": "P0",
    "category": "normal"
  }}
]

场景分类说明:
- normal: 正常场景
- exception: 异常场景
- boundary: 边界场景
- performance: 性能场景
- security: 安全场景

注意:
1. 场景要覆盖正常、异常、边界等各类情况
2. 优先级要合理(P0最高，P3最低)
3. 前置条件要明确
4. 预期结果要具体可验证
''',
                'model_params': {'temperature': 0.5, 'max_tokens': 3000},
                'is_default': True,
            },
            {
                'agent_type': 'case',
                'agent_name': '用例生成Agent',
                'model_provider': 'openai',
                'model_name': 'gpt-4',
                'prompt_template': '''你是一个专业的测试用例编写专家。请为以下场景生成详细的测试用例。

测试场景:
{scenario}

{case_template}

{available_scripts}

请按照以下JSON格式输出测试用例:
{{
  "case_id": "TC001",
  "title": "用例标题",
  "test_type": "ui",
  "priority": "P0",
  "precondition": "前置条件",
  "steps": [
    {{
      "step_no": 1,
      "action": "操作步骤",
      "data": "测试数据",
      "expected": "预期结果"
    }}
  ],
  "test_data": {{
    "username": "testuser",
    "password": "Test@123"
  }},
  "expected_result": "整体预期结果",
  "postcondition": "后置条件"
}}

注意:
1. 步骤要详细具体，可操作
2. 测试数据要真实有效
3. 预期结果要明确可验证
4. 符合SMART原则(Specific/Measurable/Achievable/Relevant/Time-bound)
5. 如需生成测试数据，使用可用脚本: {script_names}
''',
                'model_params': {'temperature': 0.4, 'max_tokens': 2500},
                'is_default': True,
            },
            {
                'agent_type': 'code',
                'agent_name': '代码生成Agent',
                'model_provider': 'openai',
                'model_name': 'gpt-4',
                'prompt_template': '''你是一个专业的自动化测试代码生成专家。请根据测试用例生成自动化测试代码。

测试用例:
{test_cases}

技术栈: {tech_stack}

请生成完整的测试代码，包括:
1. 测试代码文件
2. 配置文件
3. 依赖文件(requirements.txt或package.json)
4. README说明文档

输出格式为JSON:
{{
  "files": {{
    "test_login.py": "# 测试代码内容",
    "conftest.py": "# Pytest配置",
    "requirements.txt": "pytest==7.4.0\\nselenium==4.15.0",
    "README.md": "# 项目说明"
  }}
}}

注意:
1. 代码要规范，遵循最佳实践
2. 包含必要的注释
3. 错误处理要完善
4. 依赖版本要明确
''',
                'model_params': {'temperature': 0.3, 'max_tokens': 4000},
                'is_default': True,
            },
            {
                'agent_type': 'quality',
                'agent_name': '质量优化Agent',
                'model_provider': 'openai',
                'model_name': 'gpt-4',
                'prompt_template': '''你是一个专业的测试质量分析专家。请分析测试用例的质量并提出改进建议。

需求分析:
{requirement_analysis}

测试场景:
{scenarios}

测试用例:
{test_cases}

{defect_history}

请按照以下JSON格式输出质量报告:
{{
  "coverage_analysis": {{
    "coverage_rate": 85,
    "uncovered_points": ["未覆盖的功能点"],
    "missing_scenarios": ["缺失的场景"]
  }},
  "quality_analysis": {{
    "duplicate_cases": ["重复的用例"],
    "non_smart_cases": ["不符合SMART原则的用例"],
    "incomplete_data": ["测试数据不完整的用例"]
  }},
  "suggestions": [
    "改进建议1",
    "改进建议2"
  ],
  "quality_score": {{
    "coverage_score": 85,
    "quality_score": 78,
    "total_score": 81
  }}
}}

注意:
1. 覆盖度分析要全面
2. 质量问题要具体
3. 改进建议要可操作
4. 评分要客观合理
''',
                'model_params': {'temperature': 0.4, 'max_tokens': 3000},
                'is_default': True,
            },
        ]
    )


def downgrade() -> None:
    # Delete seeded data
    op.execute("DELETE FROM agent_configs WHERE is_default = true")
    op.execute("DELETE FROM python_scripts WHERE is_builtin = true")
