# 数据库设计文档

## 概述

本系统使用PostgreSQL作为主数据库，Redis作为缓存和会话存储。数据库设计遵循轻量级原则，中间结果存储在Redis中（24小时过期），最终确认的数据可选存储到PostgreSQL。

## 数据库表结构

### 1. agent_configs (Agent配置表)

存储各个Agent的配置信息，包括模型选择、提示词模板、参数等。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| agent_type | VARCHAR(50) | Agent类型: requirement/scenario/case/code/quality |
| agent_name | VARCHAR(255) | Agent名称 |
| model_provider | VARCHAR(50) | 模型提供商: openai/anthropic/local |
| model_name | VARCHAR(100) | 模型名称 |
| prompt_template | TEXT | 提示词模板 |
| model_params | JSONB | 模型参数: {"temperature": 0.7, "max_tokens": 2000} |
| knowledge_bases | INTEGER[] | 关联知识库ID数组 |
| scripts | INTEGER[] | 关联脚本ID数组 |
| is_default | BOOLEAN | 是否为默认配置 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 2. knowledge_bases (知识库表)

存储历史用例、缺陷库、业务规则等知识库文档。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(255) | 知识库名称 |
| type | VARCHAR(50) | 类型: case/defect/rule/api |
| storage_type | VARCHAR(50) | 存储类型: local/url/database |
| file_path | TEXT | 本地文件路径 |
| url | TEXT | 外部URL |
| content | TEXT | 文档内容 |
| metadata | JSONB | 元数据 |
| search_vector | TSVECTOR | 全文搜索向量 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- `idx_knowledge_search`: GIN索引，用于全文搜索
- `ix_knowledge_bases_type`: 类型索引

**触发器:**
- `tsvector_update`: 自动更新search_vector字段

### 3. python_scripts (Python脚本表)

存储用于生成测试数据的Python脚本。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(255) | 脚本名称（唯一） |
| description | TEXT | 脚本描述 |
| code | TEXT | 脚本代码 |
| dependencies | TEXT[] | 依赖包列表 |
| is_builtin | BOOLEAN | 是否为内置脚本 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**预置脚本:**
- `generate_phone_number`: 生成随机手机号
- `generate_email`: 生成随机邮箱
- `generate_id_card`: 生成随机身份证号
- `get_timestamp`: 获取当前时间戳
- `md5_encrypt`: MD5加密
- `generate_username`: 生成随机用户名

### 4. case_templates (用例模板表)

存储测试用例模板。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| name | VARCHAR(255) | 模板名称 |
| test_type | VARCHAR(50) | 测试类型: ui/api/unit |
| template_structure | JSONB | 模板结构 |
| is_builtin | BOOLEAN | 是否为内置模板 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### 5. test_cases (测试用例表 - 可选)

存储最终确认的测试用例（可选功能）。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键 |
| case_id | VARCHAR(50) | 用例ID |
| session_id | VARCHAR(100) | 会话ID |
| title | VARCHAR(500) | 用例标题 |
| test_type | VARCHAR(50) | 测试类型: ui/api/unit |
| priority | VARCHAR(10) | 优先级: P0/P1/P2/P3 |
| precondition | TEXT | 前置条件 |
| steps | JSONB | 测试步骤 |
| test_data | JSONB | 测试数据 |
| expected_result | TEXT | 预期结果 |
| postcondition | TEXT | 后置条件 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

**索引:**
- `idx_test_cases_session`: 会话ID索引

## Redis数据结构

Redis用于存储会话数据和中间结果，所有数据24小时自动过期。

### 会话数据结构

```
session:{session_id}:requirement_analysis  -> JSON (需求分析结果)
session:{session_id}:scenarios             -> JSON (测试场景列表)
session:{session_id}:cases                 -> JSON (测试用例列表)
session:{session_id}:code                  -> JSON (生成的代码)
session:{session_id}:quality_report        -> JSON (质量报告)
session:{session_id}:conversation          -> JSON (对话历史)
session:{session_id}:metadata              -> JSON (会话元数据)
```

## 数据库初始化

### 前置条件

1. 安装PostgreSQL 14+
2. 安装Redis 6+
3. 创建数据库:
```bash
createdb ai_test_case_generator
```

### 运行迁移

```bash
# 方法1: 使用Alembic命令
cd backend
alembic upgrade head

# 方法2: 使用初始化脚本
python scripts/init_db.py
```

### 迁移文件

- `20250115_initial_schema.py`: 创建所有表结构
- `20250115_seed_data.py`: 插入初始数据（预置脚本和Agent配置）

## 全文搜索

知识库表使用PostgreSQL的全文搜索功能：

```sql
-- 搜索示例
SELECT id, name, content, ts_rank(search_vector, query) as rank
FROM knowledge_bases, to_tsquery('simple', '登录 & 测试') query
WHERE search_vector @@ query AND type = 'case'
ORDER BY rank DESC
LIMIT 5;
```

## 数据备份

### PostgreSQL备份

```bash
# 备份
pg_dump ai_test_case_generator > backup.sql

# 恢复
psql ai_test_case_generator < backup.sql
```

### Redis备份

Redis数据为临时数据，通常不需要备份。如需备份：

```bash
# 触发RDB快照
redis-cli BGSAVE

# 备份文件位置
cp /var/lib/redis/dump.rdb /backup/redis_backup.rdb
```

## 性能优化

1. **连接池配置**
   - PostgreSQL: 20个连接
   - Redis: 10个连接

2. **索引优化**
   - 知识库全文搜索使用GIN索引
   - 常用查询字段添加B-tree索引

3. **查询优化**
   - 使用异步查询（asyncpg）
   - 批量操作使用bulk_insert
   - 合理使用LIMIT限制结果集

## 安全性

1. **SQL注入防护**: 使用参数化查询
2. **密码加密**: API密钥使用环境变量存储
3. **最小权限**: 数据库用户仅授予必要权限
4. **数据加密**: 敏感数据字段加密存储（如需要）

## 监控指标

- 数据库连接数
- 查询响应时间
- 慢查询日志
- Redis内存使用
- 会话数量
