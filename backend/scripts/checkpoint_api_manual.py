"""
Manual API Checkpoint Verification Guide
手动API检查点验证指南
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def check_api_routes():
    """检查API路由配置"""
    print_section("检查API路由配置")
    
    try:
        from app.main import app
        
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = list(route.methods) if route.methods else []
                routes.append((route.path, methods))
        
        print(f"\n✓ 共发现 {len(routes)} 个路由端点\n")
        
        # Group by category
        categories = {
            "基础": [],
            "生成": [],
            "知识库": [],
            "脚本": [],
            "Agent配置": [],
            "模板": [],
            "导出": [],
            "WebSocket": [],
        }
        
        for path, methods in routes:
            if path in ["/", "/health"]:
                categories["基础"].append((path, methods))
            elif "/generate/" in path or path in ["/api/v1/optimize", "/api/v1/supplement"]:
                categories["生成"].append((path, methods))
            elif "/knowledge-base/" in path:
                categories["知识库"].append((path, methods))
            elif "/scripts" in path:
                categories["脚本"].append((path, methods))
            elif "/agent-configs" in path:
                categories["Agent配置"].append((path, methods))
            elif "/templates" in path:
                categories["模板"].append((path, methods))
            elif "/export/" in path:
                categories["导出"].append((path, methods))
            elif "/ws/" in path:
                categories["WebSocket"].append((path, methods))
        
        for category, endpoints in categories.items():
            if endpoints:
                print(f"\n{category}接口:")
                for path, methods in endpoints:
                    methods_str = ", ".join(methods) if methods else "N/A"
                    print(f"  ✓ {methods_str:20} {path}")
        
        return True
    except Exception as e:
        print(f"✗ 检查API路由失败: {e}")
        return False


def check_api_implementations():
    """检查API实现文件"""
    print_section("检查API实现文件")
    
    api_files = [
        ("app/api/generate.py", "生成类API"),
        ("app/api/websocket.py", "WebSocket API"),
        ("app/api/knowledge_base.py", "知识库管理API"),
        ("app/api/scripts.py", "脚本管理API"),
        ("app/api/agent_configs.py", "Agent配置API"),
        ("app/api/templates.py", "用例模板API"),
        ("app/api/export.py", "导出API"),
    ]
    
    all_ok = True
    for file_path, name in api_files:
        full_path = Path(__file__).parent.parent / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✓ {name:20} - {file_path} ({size} bytes)")
        else:
            print(f"✗ {name:20} - {file_path} (不存在)")
            all_ok = False
    
    return all_ok


def print_manual_test_guide():
    """打印手动测试指南"""
    print_section("手动测试指南")
    
    print("""
要完成API检查点验证,请按以下步骤操作:

1. 启动后端服务器
   ==================
   cd backend
   uvicorn app.main:app --reload
   
   或者使用Python模块方式:
   python -m uvicorn app.main:app --reload

2. 在新终端运行自动化验证脚本
   ============================
   cd backend
   python scripts/checkpoint_api.py

3. 手动测试关键功能
   ==================
   
   a) 测试基础接口:
      curl http://localhost:8000/
      curl http://localhost:8000/health
   
   b) 测试知识库列表:
      curl http://localhost:8000/api/v1/knowledge-base/list
   
   c) 测试脚本列表:
      curl http://localhost:8000/api/v1/scripts
   
   d) 测试Agent配置列表:
      curl http://localhost:8000/api/v1/agent-configs
   
   e) 测试用例模板列表:
      curl http://localhost:8000/api/v1/templates

4. 测试文件上传
   ==============
   创建测试文件:
   echo "Test document" > test.txt
   
   上传到知识库:
   curl -X POST http://localhost:8000/api/v1/knowledge-base/upload \\
     -F "file=@test.txt" \\
     -F "name=Test Document" \\
     -F "type=case"

5. 测试WebSocket连接
   ===================
   使用WebSocket客户端工具(如wscat):
   wscat -c ws://localhost:8000/ws/generate
   
   或使用浏览器开发者工具的Console:
   const ws = new WebSocket('ws://localhost:8000/ws/generate');
   ws.onmessage = (event) => console.log(event.data);

6. 测试导出功能
   ==============
   curl -X POST http://localhost:8000/api/v1/export/cases \\
     -H "Content-Type: application/json" \\
     -d '{"format": "json", "data": []}'

注意事项:
=========
- 确保PostgreSQL和Redis服务已启动
- 确保已运行数据库初始化脚本: python scripts/init_db.py
- 生成类API需要配置LLM API密钥才能完整测试
- 某些API可能返回422(参数验证错误),这是正常的,说明端点存在
""")


def main():
    print("=" * 60)
    print("后端API检查点验证 - 手动测试指南")
    print("=" * 60)
    
    # Check API routes
    routes_ok = check_api_routes()
    
    # Check API implementation files
    files_ok = check_api_implementations()
    
    # Print manual test guide
    print_manual_test_guide()
    
    print_section("验证结果")
    
    if routes_ok and files_ok:
        print("\n✓ API路由和实现文件检查通过")
        print("✓ 所有API端点已配置")
        print("\n请按照上述指南启动服务器并进行手动测试")
        return 0
    else:
        print("\n✗ 发现问题,请检查上述失败项")
        return 1


if __name__ == "__main__":
    sys.exit(main())
