# AI测试用例生成系统

AI驱动的智能测试用例生成系统,通过多个专业Agent协作,实现从需求分析到用例生成、代码生成、质量优化的全流程自动化。

## 项目概述

本系统采用多Agent协作架构,包含5个专业Agent:
- **需求分析Agent**: 解析需求文档,提取测试关键信息
- **场景生成Agent**: 根据需求生成全面的测试场景
- **用例生成Agent**: 为每个场景生成详细测试用例
- **代码生成Agent**: 根据用例生成自动化测试代码
- **质量优化Agent**: 分析用例质量并提出改进建议

## 技术栈

### 后端
- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 14+ (全文搜索)
- **缓存**: Redis 6+
- **ORM**: SQLAlchemy 2.0 (Async)
- **LLM**: OpenAI API / Anthropic API

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI组件**: Ant Design 5
- **状态管理**: Zustand
- **代码编辑器**: Monaco Editor
- **图表**: ECharts

## 项目结构

```
.
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── main.py         # FastAPI应用入口
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic模型
│   │   ├── api/            # API路由
│   │   ├── services/       # 业务逻辑
│   │   └── agents/         # AI Agents
│   ├── alembic/            # 数据库迁移
│   ├── tests/              # 测试文件
│   └── requirements.txt    # Python依赖
│
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── main.tsx       # 应用入口
│   │   ├── App.tsx        # 根组件
│   │   ├── api/           # API客户端
│   │   ├── components/    # 通用组件
│   │   ├── pages/         # 页面组件
│   │   ├── stores/        # 状态管理
│   │   └── utils/         # 工具函数
│   └── package.json       # 前端依赖
│
└── .kiro/                 # Kiro规范文档
    └── specs/
        └── ai-test-case-generator/
            ├── requirements.md  # 需求文档
            ├── design.md       # 设计文档
            └── tasks.md        # 任务列表
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+

### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑.env文件,配置数据库、Redis和LLM API密钥

# 初始化数据库
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看API文档

### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
copy .env.example .env

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173

## 核心功能

### 1. 需求分析
- 支持Word、PDF、Markdown、URL等多种输入方式
- 自动提取功能点、业务规则、数据模型、接口定义
- 知识库辅助分析,参考历史需求

### 2. 场景生成
- 根据测试类型(UI/接口/白盒)生成对应场景
- 覆盖正常、异常、边界、性能、安全等场景
- 支持场景选择和补充

### 3. 用例生成
- 为每个场景生成详细测试用例
- 自动调用Python脚本生成测试数据
- 支持用例模板和在线编辑
- 多轮对话优化用例

### 4. 代码生成
- 根据用例生成自动化测试代码
- 支持多种技术栈(Pytest+Selenium/Requests)
- 生成完整项目结构和配置文件

### 5. 质量优化
- 分析需求覆盖度
- 识别重复和低质量用例
- 提供改进建议和质量评分

### 6. 知识库管理
- 上传历史用例、缺陷、业务规则
- PostgreSQL全文搜索
- 辅助生成更准确的用例

### 7. 脚本管理
- 在线编辑Python脚本
- 沙箱环境安全执行
- 预置常用数据生成脚本

## 开发指南

### 后端开发

```bash
# 运行测试
pytest

# 生成覆盖率报告
pytest --cov=app --cov-report=html

# 创建数据库迁移
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head
```

### 前端开发

```bash
# 运行ESLint检查
npm run lint

# 构建生产版本
npm run build

# 预览生产版本
npm run preview
```

## 部署

### 服务器要求
- CPU: 4核
- 内存: 4GB
- 磁盘: 40GB
- 操作系统: Ubuntu 20.04 / CentOS 7+

详细部署步骤请参考 [backend/README.md](backend/README.md) 和 [frontend/README.md](frontend/README.md)

## 文档

- [需求文档](.kiro/specs/ai-test-case-generator/requirements.md)
- [设计文档](.kiro/specs/ai-test-case-generator/design.md)
- [任务列表](.kiro/specs/ai-test-case-generator/tasks.md)
- [后端文档](backend/README.md)
- [前端文档](frontend/README.md)

## 许可证

MIT

## 贡献

欢迎提交Issue和Pull Request!

## 联系方式

如有问题,请提交Issue或联系项目维护者。
