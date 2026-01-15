# AI Test Case Generator - Frontend

AI驱动的智能测试用例生成系统前端应用

## 技术栈

- **框架**: React 18
- **构建工具**: Vite
- **语言**: TypeScript
- **UI组件**: Ant Design 5
- **状态管理**: Zustand
- **路由**: React Router 6
- **HTTP客户端**: Axios
- **代码编辑器**: Monaco Editor
- **图表**: ECharts

## 项目结构

```
frontend/
├── src/
│   ├── main.tsx            # 应用入口
│   ├── App.tsx             # 根组件
│   ├── api/                # API客户端
│   │   └── client.ts       # Axios配置
│   ├── components/         # 通用组件
│   ├── pages/              # 页面组件
│   ├── stores/             # Zustand状态管理
│   ├── utils/              # 工具函数
│   │   └── websocket.ts    # WebSocket客户端
│   ├── types/              # TypeScript类型定义
│   └── styles/             # 样式文件
├── public/                 # 静态资源
├── index.html             # HTML模板
├── package.json           # 项目依赖
├── tsconfig.json          # TypeScript配置
├── vite.config.ts         # Vite配置
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
copy .env.example .env

# 编辑.env文件,配置API地址
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 4. 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录

### 5. 预览生产版本

```bash
npm run preview
```

## 开发指南

### 代码规范

```bash
# 运行ESLint检查
npm run lint
```

### 目录说明

- `src/api/` - API接口定义和HTTP客户端配置
- `src/components/` - 可复用的UI组件
- `src/pages/` - 页面级组件
- `src/stores/` - Zustand状态管理
- `src/utils/` - 工具函数和辅助类
- `src/types/` - TypeScript类型定义
- `src/styles/` - 全局样式和主题配置

### 状态管理

使用Zustand进行状态管理:

```typescript
import { create } from 'zustand'

interface AppState {
  sessionId: string | null
  setSessionId: (id: string) => void
}

export const useAppStore = create<AppState>((set) => ({
  sessionId: null,
  setSessionId: (id) => set({ sessionId: id }),
}))
```

### API调用

使用配置好的axios实例:

```typescript
import apiClient from '@/api/client'

const response = await apiClient.post('/api/v1/generate/requirement', data)
```

### WebSocket连接

使用WebSocket客户端进行流式通信:

```typescript
import WebSocketClient from '@/utils/websocket'

const ws = new WebSocketClient('/ws/generate')
ws.connect(
  (message) => {
    console.log('Received:', message)
  },
  (error) => {
    console.error('Error:', error)
  }
)
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| VITE_API_BASE_URL | 后端API地址 | http://localhost:8000 |
| VITE_WS_BASE_URL | WebSocket地址 | ws://localhost:8000 |

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 许可证

MIT
