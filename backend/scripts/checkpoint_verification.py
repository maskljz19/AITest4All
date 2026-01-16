"""
Checkpoint Verification Script
验证后端核心功能是否正常工作
"""
import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.core.database import engine, AsyncSessionLocal
from app.core import redis_client as redis_module
from app.agents.requirement_agent import RequirementAgent
from app.agents.scenario_agent import ScenarioAgent
from app.agents.case_agent import CaseAgent
from app.agents.code_agent import CodeAgent
from app.agents.quality_agent import QualityAgent
from app.agents.optimize_agent import OptimizeAgent
from app.services.document_parser import DocumentParser
from app.services.script_executor import ScriptExecutor
from app.services.knowledge_base import KnowledgeBaseService
from app.services.session_manager import SessionManager
from sqlalchemy import text


class CheckpointVerifier:
    def __init__(self):
        self.results = []
        self.failed = False
    
    def log_success(self, message: str):
        print(f"✓ {message}")
        self.results.append(("SUCCESS", message))
    
    def log_failure(self, message: str, error: str = ""):
        print(f"✗ {message}")
        if error:
            print(f"  Error: {error}")
        self.results.append(("FAILURE", message, error))
        self.failed = True
    
    def log_info(self, message: str):
        print(f"ℹ {message}")
    
    async def verify_database(self):
        """验证数据库连接和表结构"""
        self.log_info("\n=== 验证数据库 ===")
        
        try:
            # Test database connection
            async with AsyncSessionLocal() as db:
                result = await db.execute(text("SELECT 1"))
                result.fetchone()
                self.log_success("数据库连接正常")
                
                # Check if tables exist
                tables = [
                    'agent_configs',
                    'knowledge_bases',
                    'python_scripts',
                    'case_templates'
                ]
                
                for table in tables:
                    result = await db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    self.log_success(f"表 {table} 存在 (记录数: {count})")
            
        except Exception as e:
            self.log_failure("数据库验证失败", str(e))
    
    async def verify_redis(self):
        """验证Redis连接和会话管理"""
        self.log_info("\n=== 验证Redis ===")
        
        try:
            # Initialize Redis
            await redis_module.init_redis()
            redis_client = redis_module.redis_client
            
            # Test Redis connection
            await redis_client.ping()
            self.log_success("Redis连接正常")
            
            # Test session manager
            session_manager = SessionManager(redis_client)
            session_id = await session_manager.create_session("test_user")
            self.log_success(f"创建会话成功: {session_id}")
            
            # Test save and retrieve
            test_data = {"test": "data", "value": 123}
            await session_manager.save_step_result(session_id, "test_step", test_data)
            self.log_success("保存会话数据成功")
            
            retrieved_data = await session_manager.get_step_result(session_id, "test_step")
            if retrieved_data == test_data:
                self.log_success("读取会话数据成功")
            else:
                self.log_failure("会话数据不匹配")
            
            # Cleanup
            await session_manager.delete_session(session_id)
            self.log_success("删除会话成功")
            
            # Close Redis
            await redis_module.close_redis()
            
        except Exception as e:
            self.log_failure("Redis验证失败", str(e))
    
    async def verify_agents(self):
        """验证所有Agent可以独立运行"""
        self.log_info("\n=== 验证Agents ===")
        
        agents = [
            ("需求分析Agent", RequirementAgent),
            ("场景生成Agent", ScenarioAgent),
            ("用例生成Agent", CaseAgent),
            ("代码生成Agent", CodeAgent),
            ("质量优化Agent", QualityAgent),
            ("优化补充Agent", OptimizeAgent)
        ]
        
        for agent_name, agent_class in agents:
            try:
                agent = agent_class()
                self.log_success(f"{agent_name} 初始化成功")
                
                # Check if agent has required methods
                if hasattr(agent, 'generate'):
                    self.log_success(f"{agent_name} 具有generate方法")
                else:
                    self.log_failure(f"{agent_name} 缺少generate方法")
                
            except Exception as e:
                self.log_failure(f"{agent_name} 初始化失败", str(e))
    
    async def verify_services(self):
        """验证核心服务"""
        self.log_info("\n=== 验证核心服务 ===")
        
        # Test DocumentParser
        try:
            parser = DocumentParser()
            # Test with simple text
            test_text = "这是一个测试文档"
            result = parser.extract_text(test_text.encode(), "txt")
            if result == test_text:
                self.log_success("文档解析服务正常")
            else:
                self.log_failure("文档解析服务返回结果不正确")
        except Exception as e:
            self.log_failure("文档解析服务失败", str(e))
        
        # Test ScriptExecutor
        try:
            executor = ScriptExecutor()
            test_script = "print('Hello, World!')\nresult = 42"
            result = executor.execute(test_script)
            if result.get('success'):
                self.log_success("脚本执行服务正常")
            else:
                self.log_failure("脚本执行服务失败", result.get('error', ''))
        except Exception as e:
            self.log_failure("脚本执行服务失败", str(e))
        
        # Test KnowledgeBaseService (requires db session)
        try:
            async with AsyncSessionLocal() as db:
                kb_service = KnowledgeBaseService(db)
                self.log_success("知识库服务初始化成功")
        except Exception as e:
            self.log_failure("知识库服务初始化失败", str(e))
    
    async def verify_configuration(self):
        """验证配置"""
        self.log_info("\n=== 验证配置 ===")
        
        try:
            # Check database URL
            if settings.database_url:
                self.log_success("数据库URL已配置")
            else:
                self.log_failure("数据库URL未配置")
            
            # Check Redis URL
            if settings.redis_url:
                self.log_success("Redis URL已配置")
            else:
                self.log_failure("Redis URL未配置")
            
            # Check OpenAI API Key (optional)
            if settings.openai_api_key:
                self.log_success("OpenAI API Key已配置")
            else:
                self.log_info("OpenAI API Key未配置 (可选)")
            
        except Exception as e:
            self.log_failure("配置验证失败", str(e))
    
    async def run_all_checks(self):
        """运行所有检查"""
        print("=" * 60)
        print("后端核心功能检查点验证")
        print("=" * 60)
        
        await self.verify_configuration()
        await self.verify_database()
        await self.verify_redis()
        await self.verify_agents()
        await self.verify_services()
        
        print("\n" + "=" * 60)
        print("验证结果汇总")
        print("=" * 60)
        
        success_count = sum(1 for r in self.results if r[0] == "SUCCESS")
        failure_count = sum(1 for r in self.results if r[0] == "FAILURE")
        
        print(f"成功: {success_count}")
        print(f"失败: {failure_count}")
        
        if self.failed:
            print("\n⚠ 发现问题,请检查上述失败项")
            return False
        else:
            print("\n✓ 所有检查通过!")
            return True


async def main():
    verifier = CheckpointVerifier()
    success = await verifier.run_all_checks()
    
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
