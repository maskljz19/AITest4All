# 快速开始指南

## 项目已完成基础架构搭建 ✅

项目结构已创建完成,包含后端(FastAPI)和前端(React + TypeScript)的完整框架。

## 下一步操作

### 1. 安装后端依赖

```bash
cd backend

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置数据库

在启动后端之前,需要先配置PostgreSQL和Redis:

#### PostgreSQL设置
```bash
# 创建数据库
createdb ai_test_case_generator

# 或使用psql
psql -U postgres
CREATE DATABASE ai_test_case_generator;
\q
```

#### 更新数据库连接
编辑 `backend/.env` 文件,更新数据库连接字符串:
```
DATABASE_URL=postgresql://你的用户名:你的密码@localhost:5432/ai_test_case_generator
```

### 3. 配置LLM API密钥

编辑 `backend/.env` 文件,添加你的API密钥:
```
OPENAI_API_KEY=sk-your-actual-openai-key
ANTHROPIC_API_KEY=your-actual-anthropic-key
```

### 4. 初始化数据库

```bash
# 在backend目录下
alembic upgrade head
```

### 5. 启动后端服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看API文档

### 6. 安装前端依赖

打开新的终端窗口:

```bash
cd frontend

# 安装依赖
npm install
```

### 7. 启动前端服务

```bash
npm run dev
```

访问 http://localhost:5173

## 项目结构说明

### 后端结构
```
backend/
├── app/
│   ├── main.py              # FastAPI应用入口
│   ├── core/                # 核心配置
│   │   ├── config.py        # 环境变量配置
│   │   ├── database.py      # PostgreSQL连接
│   │   └── redis_client.py  # Redis连接
│   ├── models/              # 数据库模型 (待实现)
│   ├── schemas/             # Pydantic模型 (待实现)
│   ├── api/                 # API路由 (待实现)
│   ├── services/            # 业务逻辑 (待实现)
│   └── agents/              # AI Agents (待实现)
├── alembic/                 # 数据库迁移
├── tests/                   # 测试文件
└── requirements.txt         # Python依赖
```

### 前端结构
```
frontend/
├── src/
│   ├── main.tsx            # 应用入口
│   ├── App.tsx             # 根组件
│   ├── api/                # API客户端
│   │   └── client.ts       # Axios配置
│   ├── components/         # 通用组件 (待实现)
│   ├── pages/              # 页面组件 (待实现)
│   ├── stores/             # Zustand状态管理 (待实现)
│   ├── utils/              # 工具函数
│   │   └── websocket.ts    # WebSocket客户端
│   └── types/              # TypeScript类型 (待实现)
└── package.json            # 前端依赖
```

## 已配置的功能

### 后端
✅ FastAPI应用框架  
✅ PostgreSQL异步连接 (SQLAlchemy 2.0)  
✅ Redis异步连接  
✅ Alembic数据库迁移  
✅ 环境变量管理  
✅ CORS中间件  
✅ 健康检查端点  

### 前端
✅ React 18 + TypeScript  
✅ Vite构建工具  
✅ Ant Design 5 UI组件库  
✅ React Router路由  
✅ Axios HTTP客户端  
✅ WebSocket客户端  
✅ API代理配置  

## 下一个任务

根据任务列表,下一步应该执行:

**任务2: 数据库设计与初始化**
- 创建数据库表结构
- 创建数据库迁移脚本
- 编写数据库操作单元测试

## 常见问题

### Q: 如何检查后端是否正常运行?
A: 访问 http://localhost:8000/health ,应该返回 `{"status": "healthy"}`

### Q: 前端无法连接后端?
A: 检查:
1. 后端是否在8000端口运行
2. 前端的 `.env` 文件中API地址是否正确
3. Vite的代理配置是否正确

### Q: 数据库连接失败?
A: 检查:
1. PostgreSQL服务是否启动
2. 数据库是否已创建
3. `.env` 文件中的连接字符串是否正确
4. 用户名和密码是否正确

### Q: Redis连接失败?
A: 检查:
1. Redis服务是否启动
2. Redis端口是否为6379
3. `.env` 文件中的Redis URL是否正确

## 技术支持

如遇到问题,请查看:
- [后端文档](backend/README.md)
- [前端文档](frontend/README.md)
- [需求文档](.kiro/specs/ai-test-case-generator/requirements.md)
- [设计文档](.kiro/specs/ai-test-case-generator/design.md)
- [任务列表](.kiro/specs/ai-test-case-generator/tasks.md)
