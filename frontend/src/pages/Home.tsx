import React from 'react'
import { Card, Row, Col, Statistic, Button } from 'antd'
import { useNavigate } from 'react-router-dom'
import {
  FileTextOutlined,
  ExperimentOutlined,
  DatabaseOutlined,
  CodeOutlined,
} from '@ant-design/icons'

const Home: React.FC = () => {
  const navigate = useNavigate()

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>欢迎使用AI测试用例生成系统</h1>
      
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="生成的用例"
              value={0}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="知识库文档"
              value={0}
              prefix={<DatabaseOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="自定义脚本"
              value={0}
              prefix={<CodeOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="生成会话"
              value={0}
              prefix={<ExperimentOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card title="快速开始" style={{ marginBottom: 24 }}>
        <p style={{ marginBottom: 16 }}>
          通过AI驱动的多Agent协作，从需求分析到用例生成、代码生成、质量优化的全流程自动化。
        </p>
        <Button
          type="primary"
          size="large"
          icon={<ExperimentOutlined />}
          onClick={() => navigate('/generate')}
        >
          开始生成测试用例
        </Button>
      </Card>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={12}>
          <Card title="功能特性" size="small">
            <ul style={{ paddingLeft: 20 }}>
              <li>智能需求分析：自动提取测试关键信息</li>
              <li>场景生成：覆盖正常、异常、边界等各类情况</li>
              <li>用例生成：生成详细的测试步骤和数据</li>
              <li>代码生成：自动生成自动化测试代码</li>
              <li>质量优化：分析用例质量并提出改进建议</li>
            </ul>
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="使用流程" size="small">
            <ul style={{ paddingLeft: 20 }}>
              <li>1. 上传需求文档或输入需求文本</li>
              <li>2. 系统自动分析需求并生成测试场景</li>
              <li>3. 为每个场景生成详细测试用例</li>
              <li>4. 可选：生成自动化测试代码</li>
              <li>5. 质量分析并导出结果</li>
            </ul>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Home
