# AI测试用例生成系统

> 基于AI的智能测试用例生成平台，通过多Agent协作实现从需求分析到用例生成、代码生成、质量优化的全流程自动化

## 📋 项目简介

AI测试用例生成系统是一个创新的测试自动化工具，利用大语言模型(LLM)的强大能力，帮助测试工程师快速生成高质量的测试用例。系统采用多Agent协作架构，包含需求分析、场景生成、用例生成、代码生成和质量优化五个专业Agent，实现测试用例设计的智能化和标准化。

### 核心特性

- **🤖 多Agent协作**: 5个专业Agent分工协作，各司其职
- **🎯 全流程覆盖**: 需求分析 → 场景设计 → 用例生成 → 代码生成 → 质量优化
- **🔧 高度可定制**: 支持自定义提示词、模型配置和生成流程
- **📚 知识库增强**: 历史用例、缺陷库、业务规则辅助生成
- **💬 交互式优化**: 支持多轮对话，逐步优化用例质量
- **📤 多格式导出**: 支持Excel、Word、JSON、Markdown等多种格式
- **⚡ 轻量部署**: 适配4核4G40G服务器，支持本地知识库

### 适用场景

- **UI测试**: Web应用界面测试用例生成
- **接口测试**: RESTful API测试用例生成
- **白盒测试**: 单元测试用例生成
- **性能测试**: 性能测试场景设计
- **安全测试**: 安全测试用例生成

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────┐
│                   前端交互层                         │
│  用例生成向导 | Agent配置 | 知识库管理 | 脚本管理   │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                 AI Agent编排层                       │
│  需求分析 | 场景生成 | 用例生成 | 代码生成 | 质量优化│
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                  LLM服务层                           │
│  OpenAI API | Anthropic API | 本地模型              │
└────────────────────┬────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────┐
│                 数据与知识层                         │
│  知识库 | 脚本库 | 模板库 | PostgreSQL | Redis      │
└─────────────────────────────────────────────────────┘
```

## 💻 技术栈

### 后端
- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 14+
- **缓存**: Redis 6+
- **ORM**: SQLAlchemy 2.0 (Async)
- **LLM**: OpenAI API / Anthropic API
- **向量数据库**: Chroma (知识库检索)

### 前端
- **框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI组件**: Ant Design 5
- **状态管理**: Zustand
- **代码编辑器**: Monaco Editor
- **图表**: ECharts

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- OpenAI API Key 或 Anthropic API Key

### 后端部署

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env 文件，配置数据库、Redis和LLM API密钥

# 初始化数据库
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看API文档

### 前端部署

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 配置环境变量
copy .env.example .env

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173

### Docker部署

```bash
# 使用Docker Compose一键部署
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 📖 文档导航

- [用户指南](./用户指南.md) - 系统使用说明和操作指南
- [开发者文档](./开发者文档.md) - 开发环境搭建和代码结构说明
- [接口文档](./接口文档.md) - API接口详细说明
- [部署运维文档](./部署运维文档.md) - 生产环境部署和运维指南
- [工具使用文档](./工具使用文档.md) - 知识库、脚本、模板等工具使用说明

## 🎯 核心功能

### 1. 需求分析
- 支持Word、PDF、Markdown、URL等多种输入方式
- 自动提取功能点、业务规则、数据模型、接口定义
- 知识库辅助分析，参考历史需求

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

## 🔧 配置说明

### 环境变量配置

主要环境变量说明：

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/ai_test_case_generator
REDIS_URL=redis://localhost:6379/0

# LLM配置
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
DEFAULT_MODEL_PROVIDER=openai
DEFAULT_MODEL_NAME=gpt-4

# 应用配置
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
SESSION_EXPIRE_HOURS=24
MAX_UPLOAD_SIZE_MB=10
```

详细配置说明请参考 [开发者文档](./开发者文档.md)

## 📊 项目结构

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
│   │   ├── agents/         # AI Agents
│   │   ├── tools/          # 工具模块
│   │   └── mcp/            # MCP服务器
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
├── deployment/             # 部署配置
│   ├── nginx/             # Nginx配置
│   ├── supervisor/        # Supervisor配置
│   ├── systemd/           # Systemd配置
│   └── scripts/           # 部署脚本
│
├── agent_prompts/          # Agent提示词
├── docker-compose.yml      # Docker编排
└── README.md              # 项目说明
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

### 代码规范

- Python代码遵循PEP 8规范
- TypeScript代码遵循ESLint配置
- 提交信息遵循Conventional Commits规范

## 📝 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 📧 联系方式

如有问题或建议，请提交Issue或联系项目维护者。

## 🙏 致谢

感谢所有为本项目做出贡献的开发者！

---

**注意**: 本系统需要配置OpenAI或Anthropic的API密钥才能正常使用。请确保您已经获取相应的API密钥并正确配置。
