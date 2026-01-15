"""
简化的检查点验证脚本
验证后端核心功能 - 不依赖外部服务
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_agents():
    """检查所有Agent是否可以初始化"""
    print("\n=== 检查 Agents ===")
    
    try:
        from app.agents.requirement_agent import RequirementAgent
        from app.agents.scenario_agent import ScenarioAgent
        from app.agents.case_agent import CaseAgent
        from app.agents.code_agent import CodeAgent
        from app.agents.quality_agent import QualityAgent
        from app.agents.optimize_agent import OptimizeAgent
        
        agents = [
            ("需求分析Agent", RequirementAgent),
            ("场景生成Agent", ScenarioAgent),
            ("用例生成Agent", CaseAgent),
            ("代码生成Agent", CodeAgent),
            ("质量优化Agent", QualityAgent),
            ("优化补充Agent", OptimizeAgent)
        ]
        
        all_ok = True
        for agent_name, agent_class in agents:
            try:
                agent = agent_class()
                if hasattr(agent, 'generate'):
                    print(f"✓ {agent_name} - 初始化成功,具有generate方法")
                else:
                    print(f"✗ {agent_name} - 缺少generate方法")
                    all_ok = False
            except Exception as e:
                print(f"✗ {agent_name} - 初始化失败: {e}")
                all_ok = False
        
        return all_ok
    except Exception as e:
        print(f"✗ Agent导入失败: {e}")
        return False


def check_services():
    """检查核心服务"""
    print("\n=== 检查核心服务 ===")
    
    all_ok = True
    
    # Check DocumentParser
    try:
        from app.services.document_parser import DocumentParser
        parser = DocumentParser()
        test_text = "测试文档"
        result = parser.extract_text(test_text.encode(), "txt")
        if result == test_text:
            print("✓ 文档解析服务 - 正常")
        else:
            print("✗ 文档解析服务 - 返回结果不正确")
            all_ok = False
    except Exception as e:
        print(f"✗ 文档解析服务 - 失败: {e}")
        all_ok = False
    
    # Check ScriptExecutor
    try:
        from app.services.script_executor import ScriptExecutor
        executor = ScriptExecutor()
        test_script = "result = 1 + 1"
        result = executor.execute(test_script)
        if result.get('success'):
            print("✓ 脚本执行服务 - 正常")
        else:
            print(f"✗ 脚本执行服务 - 失败: {result.get('error', '')}")
            all_ok = False
    except Exception as e:
        print(f"✗ 脚本执行服务 - 失败: {e}")
        all_ok = False
    
    return all_ok


def check_models():
    """检查数据模型是否可以导入"""
    print("\n=== 检查数据模型 ===")
    
    try:
        from app.models import (
            AgentConfig,
            KnowledgeBase,
            PythonScript,
            CaseTemplate,
            TestCase,
        )
        print("✓ 所有数据模型导入成功")
        return True
    except Exception as e:
        print(f"✗ 数据模型导入失败: {e}")
        return False


def check_configuration():
    """检查配置"""
    print("\n=== 检查配置 ===")
    
    try:
        from app.core.config import settings
        
        print(f"✓ 配置加载成功")
        print(f"  - 数据库URL: {settings.database_url[:30]}...")
        print(f"  - Redis URL: {settings.redis_url}")
        print(f"  - 应用环境: {settings.app_env}")
        print(f"  - OpenAI API Key: {'已配置' if settings.openai_api_key and settings.openai_api_key != 'your_openai_api_key_here' else '未配置'}")
        
        return True
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False


def check_database_schema():
    """检查数据库表定义"""
    print("\n=== 检查数据库表定义 ===")
    
    try:
        from app.core.database import Base
        from app.models import (
            AgentConfig,
            KnowledgeBase,
            PythonScript,
            CaseTemplate,
            TestCase,
        )
        
        tables = Base.metadata.tables.keys()
        print(f"✓ 数据库表定义正常,共 {len(tables)} 个表:")
        for table in tables:
            print(f"  - {table}")
        
        return True
    except Exception as e:
        print(f"✗ 数据库表定义检查失败: {e}")
        return False


def main():
    print("=" * 60)
    print("后端核心功能检查点验证")
    print("=" * 60)
    
    results = []
    
    # Run all checks
    results.append(("配置", check_configuration()))
    results.append(("数据模型", check_models()))
    results.append(("数据库表定义", check_database_schema()))
    results.append(("Agents", check_agents()))
    results.append(("核心服务", check_services()))
    
    # Summary
    print("\n" + "=" * 60)
    print("验证结果汇总")
    print("=" * 60)
    
    success_count = sum(1 for _, ok in results if ok)
    total_count = len(results)
    
    for name, ok in results:
        status = "✓ 通过" if ok else "✗ 失败"
        print(f"{name}: {status}")
    
    print(f"\n总计: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print("\n✓ 所有核心功能检查通过!")
        print("\n注意事项:")
        print("- 数据库和Redis服务需要在运行时启动")
        print("- 如需测试数据库连接,请运行: python scripts/verify_db.py")
        print("- 如需初始化数据库,请运行: python scripts/init_db.py")
        return 0
    else:
        print("\n⚠ 部分检查未通过,请检查上述失败项")
        return 1


if __name__ == "__main__":
    sys.exit(main())
