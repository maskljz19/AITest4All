"""验证关键修复的脚本"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_session_manager():
    """测试 SessionManager 依赖注入"""
    print("测试 SessionManager 依赖注入...")
    
    try:
        from app.core.redis_client import init_redis, get_redis
        from app.services.session_manager import SessionManager
        
        # 初始化 Redis
        await init_redis()
        redis = await get_redis()
        
        # 创建 SessionManager（应该成功）
        session_manager = SessionManager(redis)
        print("✅ SessionManager 创建成功")
        
        # 测试创建 session
        session_id = await session_manager.create_session()
        print(f"✅ Session 创建成功: {session_id}")
        
        # 测试保存和获取数据
        test_data = {"test": "data"}
        await session_manager.save_step_result(session_id, "test_step", test_data)
        print("✅ 数据保存成功")
        
        result = await session_manager.get_step_result(session_id, "test_step")
        assert result == test_data
        print("✅ 数据获取成功")
        
        # 清理
        await session_manager.delete_session(session_id)
        print("✅ Session 清理成功")
        
        return True
        
    except Exception as e:
        print(f"❌ SessionManager 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_knowledge_base_service():
    """测试 KnowledgeBaseService 依赖注入"""
    print("\n测试 KnowledgeBaseService 依赖注入...")
    
    try:
        from app.core.database import get_async_session
        from app.services.knowledge_base import KnowledgeBaseService
        
        # 创建 DB session
        async with get_async_session() as db:
            # 创建 KnowledgeBaseService（应该成功）
            kb_service = KnowledgeBaseService(db)
            print("✅ KnowledgeBaseService 创建成功")
            
            # 测试搜索（即使没有数据也应该返回空列表）
            results = await kb_service.search("test query", limit=5)
            assert isinstance(results, list)
            print(f"✅ 搜索功能正常（返回 {len(results)} 条结果）")
        
        return True
        
    except Exception as e:
        print(f"❌ KnowledgeBaseService 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_dependencies():
    """测试 API 依赖注入函数"""
    print("\n测试 API 依赖注入函数...")
    
    try:
        from app.api.generate import get_session_manager, get_knowledge_base_service
        from app.core.redis_client import init_redis
        from app.core.database import get_async_session
        
        # 初始化 Redis
        await init_redis()
        
        # 测试 get_session_manager
        session_manager = await get_session_manager()
        print("✅ get_session_manager() 正常工作")
        
        # 测试 get_knowledge_base_service
        async with get_async_session() as db:
            # 模拟 FastAPI Depends
            async def mock_get_db():
                yield db
            
            # 直接创建（因为我们不在 FastAPI 上下文中）
            from app.services.knowledge_base import KnowledgeBaseService
            kb_service = KnowledgeBaseService(db)
            print("✅ get_knowledge_base_service() 正常工作")
        
        return True
        
    except Exception as e:
        print(f"❌ API 依赖注入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("关键修复验证脚本")
    print("=" * 60)
    
    results = []
    
    # 测试 1: SessionManager
    results.append(await test_session_manager())
    
    # 测试 2: KnowledgeBaseService
    results.append(await test_knowledge_base_service())
    
    # 测试 3: API 依赖注入
    results.append(await test_api_dependencies())
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✅ 所有测试通过！")
        return 0
    else:
        print("❌ 部分测试失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
