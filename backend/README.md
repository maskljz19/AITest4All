# AI Test Case Generator - Backend

AI驱动的智能测试用例生成系统后端服务

## 技术栈

- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 14+
- **缓存**: Redis 6+
- **ORM**: SQLAlchemy 2.0 (Async)
- **迁移**: Alembic
- **LLM**: OpenAI API / Anthropic API

## 项目结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI应用入口
│   ├── core/                # 核心配置
│   │   ├── config.py        # 配置管理
│   │   ├── database.py      # 数据库连接
│   │   └── redis_client.py  # Redis客户端
│   ├── models/              # 数据库模型
│   ├── schemas/             # Pydantic模型
│   ├── api/                 # API路由
│   ├── services/            # 业务逻辑
│   └── agents/              # AI Agents
├── alembic/                 # 数据库迁移
├── tests/                   # 测试文件
├── requirements.txt         # Python依赖
├── .env.example            # 环境变量示例
└── README.md
```

## 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
copy .env.example .env

# 编辑.env文件,配置数据库、Redis和LLM API密钥
```

### 3. 初始化数据库

```bash
# 创建数据库
# 使用PostgreSQL客户端或命令行创建数据库
createdb ai_test_case_generator

# 运行数据库迁移
alembic upgrade head
```

### 4. 启动服务

```bash
# 开发模式
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. 访问API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 开发指南

### 运行测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/test_agents.py
```

### 数据库迁移

```bash
# 创建新的迁移
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## API端点

### 核心端点

- `GET /` - 根路径
- `GET /health` - 健康检查

### 生成端点 (待实现)

- `POST /api/v1/generate/requirement` - 需求分析
- `POST /api/v1/generate/scenario` - 场景生成
- `POST /api/v1/generate/case` - 用例生成
- `POST /api/v1/generate/code` - 代码生成
- `POST /api/v1/generate/quality` - 质量分析

### 管理端点 (待实现)

- `POST /api/v1/knowledge-base/upload` - 上传知识库文档
- `GET /api/v1/knowledge-base/list` - 知识库列表
- `POST /api/v1/scripts` - 创建脚本
- `GET /api/v1/scripts` - 脚本列表

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | PostgreSQL连接字符串 | postgresql://postgres:password@localhost:5432/ai_test_case_generator |
| REDIS_URL | Redis连接字符串 | redis://localhost:6379/0 |
| OPENAI_API_KEY | OpenAI API密钥 | - |
| ANTHROPIC_API_KEY | Anthropic API密钥 | - |
| APP_ENV | 应用环境 | development |
| SESSION_EXPIRE_HOURS | 会话过期时间(小时) | 24 |
| MAX_UPLOAD_SIZE_MB | 最大上传文件大小(MB) | 10 |
| SCRIPT_TIMEOUT_SECONDS | 脚本执行超时时间(秒) | 30 |

## 许可证

MIT
