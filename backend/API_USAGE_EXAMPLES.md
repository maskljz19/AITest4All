# API Usage Examples

## Prerequisites

1. Start the server:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Ensure PostgreSQL and Redis are running
3. Configure environment variables in `.env`

## REST API Examples

### 1. Requirement Analysis

#### Using Text Input
```bash
curl -X POST "http://localhost:8000/api/v1/generate/requirement" \
  -F "requirement_text=用户登录功能：用户可以使用用户名和密码登录系统" \
  -F "test_type=ui"
```

#### Using File Upload
```bash
curl -X POST "http://localhost:8000/api/v1/generate/requirement" \
  -F "file=@requirement.docx" \
  -F "test_type=api"
```

#### Using URL
```bash
curl -X POST "http://localhost:8000/api/v1/generate/requirement" \
  -F "url=https://example.com/requirements.md" \
  -F "test_type=ui" \
  -F "knowledge_base_ids=1,2,3"
```

#### Response Example
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "function_points": [
    "用户登录",
    "密码验证",
    "会话管理"
  ],
  "business_rules": [
    "密码必须包含字母和数字",
    "登录失败3次后锁定账户"
  ],
  "data_models": [
    {
      "entity": "User",
      "fields": ["username", "password", "email"]
    }
  ],
  "api_definitions": [
    {
      "method": "POST",
      "url": "/api/login",
      "description": "用户登录接口"
    }
  ],
  "test_focus": [
    "登录流程",
    "密码加密",
    "会话管理"
  ],
  "risk_points": [
    "SQL注入",
    "密码泄露",
    "并发登录"
  ]
}
```

### 2. Scenario Generation

```bash
curl -X POST "http://localhost:8000/api/v1/generate/scenario" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "requirement_analysis": {
      "function_points": ["用户登录"],
      "business_rules": ["密码必须包含字母和数字"],
      "test_focus": ["登录流程"]
    },
    "test_type": "ui"
  }'
```

#### Response Example
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "scenarios": [
    {
      "scenario_id": "S001",
      "name": "用户登录-正常流程",
      "description": "用户使用正确的用户名和密码登录系统",
      "precondition": "用户已注册",
      "expected_result": "登录成功，跳转到首页",
      "priority": "P0",
      "category": "normal"
    },
    {
      "scenario_id": "S002",
      "name": "用户登录-密码错误",
      "description": "用户输入错误的密码",
      "precondition": "用户已注册",
      "expected_result": "显示密码错误提示",
      "priority": "P0",
      "category": "exception"
    }
  ]
}
```

### 3. Case Generation

```bash
curl -X POST "http://localhost:8000/api/v1/generate/case" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "scenarios": [
      {
        "scenario_id": "S001",
        "name": "用户登录-正常流程",
        "description": "用户使用正确的用户名和密码登录系统",
        "precondition": "用户已注册",
        "expected_result": "登录成功，跳转到首页",
        "priority": "P0",
        "category": "normal"
      }
    ]
  }'
```

### 4. Code Generation

```bash
curl -X POST "http://localhost:8000/api/v1/generate/code" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "test_cases": [...],
    "use_default_stack": true
  }'
```

### 5. Quality Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/generate/quality" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "requirement_analysis": {...},
    "scenarios": [...],
    "test_cases": [...]
  }'
```

### 6. Case Optimization

```bash
curl -X POST "http://localhost:8000/api/v1/generate/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "selected_cases": [...],
    "instruction": "请增加更多的边界条件测试"
  }'
```

### 7. Case Supplement

```bash
curl -X POST "http://localhost:8000/api/v1/generate/supplement" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "existing_cases": [...],
    "requirement": "需要补充性能测试场景"
  }'
```

## WebSocket Example

### JavaScript/TypeScript Client

```typescript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/generate');

ws.onopen = () => {
  console.log('WebSocket connected');
  
  // Send generation request
  ws.send(JSON.stringify({
    action: 'requirement',
    session_id: '550e8400-e29b-41d4-a716-446655440000',
    data: {
      requirement_text: '用户登录功能',
      test_type: 'ui',
      knowledge_base_ids: []
    }
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  switch (message.type) {
    case 'chunk':
      // Append content chunk to display
      console.log('Chunk:', message.content);
      break;
      
    case 'progress':
      // Update progress bar
      console.log('Progress:', message.metadata.progress + '%');
      break;
      
    case 'done':
      // Generation complete
      console.log('Generation complete');
      break;
      
    case 'error':
      // Handle error
      console.error('Error:', message.error);
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};
```

### Python Client

```python
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/generate"
    
    async with websockets.connect(uri) as websocket:
        # Send request
        await websocket.send(json.dumps({
            "action": "requirement",
            "session_id": "550e8400-e29b-41d4-a716-446655440000",
            "data": {
                "requirement_text": "用户登录功能",
                "test_type": "ui",
                "knowledge_base_ids": []
            }
        }))
        
        # Receive messages
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data["type"] == "chunk":
                    print(f"Chunk: {data['content']}", end='', flush=True)
                elif data["type"] == "progress":
                    print(f"\nProgress: {data['metadata']['progress']}%")
                elif data["type"] == "done":
                    print("\nGeneration complete")
                    break
                elif data["type"] == "error":
                    print(f"\nError: {data['error']}")
                    break
                    
            except websockets.exceptions.ConnectionClosed:
                break

# Run the test
asyncio.run(test_websocket())
```

## Complete Workflow Example

```bash
# 1. Analyze requirement
SESSION_ID=$(curl -X POST "http://localhost:8000/api/v1/generate/requirement" \
  -F "requirement_text=用户登录功能" \
  -F "test_type=ui" | jq -r '.session_id')

echo "Session ID: $SESSION_ID"

# 2. Generate scenarios
curl -X POST "http://localhost:8000/api/v1/generate/scenario" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"requirement_analysis\": {...},
    \"test_type\": \"ui\"
  }" > scenarios.json

# 3. Generate test cases
curl -X POST "http://localhost:8000/api/v1/generate/case" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"scenarios\": $(cat scenarios.json | jq '.scenarios')
  }" > cases.json

# 4. Generate code
curl -X POST "http://localhost:8000/api/v1/generate/code" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"test_cases\": $(cat cases.json | jq '.test_cases'),
    \"use_default_stack\": true
  }" > code.json

# 5. Analyze quality
curl -X POST "http://localhost:8000/api/v1/generate/quality" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"requirement_analysis\": {...},
    \"scenarios\": $(cat scenarios.json | jq '.scenarios'),
    \"test_cases\": $(cat cases.json | jq '.test_cases')
  }" > quality.json
```

## Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "error_code": "INVALID_INPUT",
  "message": "Must provide file, url, or requirement_text"
}
```

#### 400 Session Expired
```json
{
  "error_code": "SESSION_EXPIRED",
  "message": "Session not found or expired"
}
```

#### 500 LLM API Error
```json
{
  "error_code": "LLM_API_ERROR",
  "message": "Failed to analyze requirement: API rate limit exceeded",
  "retry_after": 5
}
```

## API Documentation

Access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
