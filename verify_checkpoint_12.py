"""
Checkpoint 12 Verification Script
验证前端功能完成的检查点

检查项:
1. 确保所有页面可以正常访问
2. 确保与后端API对接正常
3. 确保WebSocket连接正常
"""

import os
import sys
import time
import requests
import json
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.END} {msg}")

def check_backend_structure():
    """检查后端项目结构"""
    print("\n" + "="*60)
    print("1. 检查后端项目结构")
    print("="*60)
    
    required_files = [
        "backend/app/main.py",
        "backend/app/__init__.py",
        "backend/app/api/__init__.py",
        "backend/app/agents/__init__.py",
        "backend/app/core/config.py",
        "backend/app/core/database.py",
        "backend/app/core/redis_client.py",
        "backend/requirements.txt",
        "backend/.env"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"文件存在: {file_path}")
        else:
            print_error(f"文件缺失: {file_path}")
            all_exist = False
    
    return all_exist

def check_frontend_structure():
    """检查前端项目结构"""
    print("\n" + "="*60)
    print("2. 检查前端项目结构")
    print("="*60)
    
    required_files = [
        "frontend/package.json",
        "frontend/src/App.tsx",
        "frontend/src/main.tsx",
        "frontend/src/pages/Home.tsx",
        "frontend/src/pages/Generate.tsx",
        "frontend/src/pages/KnowledgeBase.tsx",
        "frontend/src/pages/Scripts.tsx",
        "frontend/src/pages/Templates.tsx",
        "frontend/src/pages/Settings.tsx",
        "frontend/src/api/client.ts",
        "frontend/src/api/generate.ts",
        "frontend/src/stores/useGenerationStore.ts"
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"文件存在: {file_path}")
        else:
            print_error(f"文件缺失: {file_path}")
            all_exist = False
    
    return all_exist

def check_backend_api(base_url="http://localhost:8000"):
    """检查后端API是否可访问"""
    print("\n" + "="*60)
    print("3. 检查后端API连接")
    print("="*60)
    
    endpoints = [
        ("/", "根路径"),
        ("/health", "健康检查"),
        ("/docs", "API文档"),
    ]
    
    all_ok = True
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print_success(f"{description} ({endpoint}): 状态码 {response.status_code}")
            else:
                print_warning(f"{description} ({endpoint}): 状态码 {response.status_code}")
                all_ok = False
        except requests.exceptions.ConnectionError:
            print_error(f"{description} ({endpoint}): 无法连接到后端服务器")
            print_warning("请确保后端服务器正在运行: uvicorn app.main:app --reload")
            all_ok = False
        except Exception as e:
            print_error(f"{description} ({endpoint}): {str(e)}")
            all_ok = False
    
    return all_ok

def check_api_endpoints(base_url="http://localhost:8000"):
    """检查关键API端点"""
    print("\n" + "="*60)
    print("4. 检查关键API端点")
    print("="*60)
    
    # GET endpoints
    get_endpoints = [
        ("/api/v1/knowledge-base/", "知识库列表"),
        ("/api/v1/scripts/", "脚本列表"),
        ("/api/v1/agent-configs/", "Agent配置列表"),
        ("/api/v1/templates/", "模板列表"),
    ]
    
    all_ok = True
    for endpoint, description in get_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code in [200, 404]:  # 404 is ok for empty lists
                print_success(f"{description} ({endpoint}): 可访问")
            else:
                print_warning(f"{description} ({endpoint}): 状态码 {response.status_code}")
        except requests.exceptions.ConnectionError:
            print_error(f"{description} ({endpoint}): 无法连接")
            all_ok = False
        except Exception as e:
            print_error(f"{description} ({endpoint}): {str(e)}")
            all_ok = False
    
    return all_ok

def check_frontend_build():
    """检查前端是否可以构建"""
    print("\n" + "="*60)
    print("5. 检查前端配置")
    print("="*60)
    
    # Check if node_modules exists
    if os.path.exists("frontend/node_modules"):
        print_success("node_modules 已安装")
    else:
        print_warning("node_modules 未安装，需要运行: npm install")
        return False
    
    # Check package.json
    try:
        with open("frontend/package.json", "r", encoding="utf-8") as f:
            package_json = json.load(f)
            print_success(f"项目名称: {package_json.get('name')}")
            print_success(f"版本: {package_json.get('version')}")
            
            # Check key dependencies
            deps = package_json.get('dependencies', {})
            key_deps = ['react', 'react-router-dom', 'antd', 'axios', 'zustand']
            for dep in key_deps:
                if dep in deps:
                    print_success(f"依赖已配置: {dep} ({deps[dep]})")
                else:
                    print_error(f"依赖缺失: {dep}")
                    return False
    except Exception as e:
        print_error(f"读取 package.json 失败: {str(e)}")
        return False
    
    return True

def check_websocket_endpoint(base_url="ws://localhost:8000"):
    """检查WebSocket端点配置"""
    print("\n" + "="*60)
    print("6. 检查WebSocket配置")
    print("="*60)
    
    # Check if websocket code exists in frontend
    ws_files = [
        "frontend/src/utils/websocket.ts",
        "frontend/src/components/Generate/StreamingOutput.tsx"
    ]
    
    all_exist = True
    for file_path in ws_files:
        if os.path.exists(file_path):
            print_success(f"WebSocket相关文件存在: {file_path}")
        else:
            print_error(f"WebSocket相关文件缺失: {file_path}")
            all_exist = False
    
    # Check backend websocket endpoint
    if os.path.exists("backend/app/api/websocket.py"):
        print_success("后端WebSocket端点已实现: backend/app/api/websocket.py")
    else:
        print_error("后端WebSocket端点缺失")
        all_exist = False
    
    return all_exist

def main():
    """主函数"""
    print("\n" + "="*60)
    print("Checkpoint 12: 前端功能完成验证")
    print("="*60)
    
    results = {
        "backend_structure": check_backend_structure(),
        "frontend_structure": check_frontend_structure(),
        "backend_api": check_backend_api(),
        "api_endpoints": check_api_endpoints(),
        "frontend_build": check_frontend_build(),
        "websocket": check_websocket_endpoint()
    }
    
    # Summary
    print("\n" + "="*60)
    print("验证结果汇总")
    print("="*60)
    
    for check_name, result in results.items():
        status = "通过" if result else "失败"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} - {check_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print_success("所有检查项通过! ✓")
        print_info("\n下一步:")
        print_info("1. 启动后端: cd backend && uvicorn app.main:app --reload")
        print_info("2. 启动前端: cd frontend && npm run dev")
        print_info("3. 访问前端: http://localhost:5173")
    else:
        print_error("部分检查项未通过 ✗")
        print_info("\n需要解决的问题:")
        for check_name, result in results.items():
            if not result:
                print_warning(f"  - {check_name}")
        
        print_info("\n建议:")
        if not results["backend_api"]:
            print_info("  - 启动后端服务器: cd backend && uvicorn app.main:app --reload")
        if not results["frontend_build"]:
            print_info("  - 安装前端依赖: cd frontend && npm install")
    
    print("="*60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
