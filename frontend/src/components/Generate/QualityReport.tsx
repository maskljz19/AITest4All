/**
 * Quality Report Component
 * 质量报告组件 - 覆盖度图表、质量分析、改进建议、评分
 */
import React from 'react'
import { Card, Row, Col, Progress, List, Tag, Statistic, Alert, Empty } from 'antd'
import {
  CheckCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  TrophyOutlined,
} from '@ant-design/icons'
import ReactECharts from 'echarts-for-react'
import type { EChartsOption } from 'echarts'
import { QualityReport as QualityReportType } from '@/types'

interface QualityReportProps {
  report: QualityReportType | null
}

const QualityReport: React.FC<QualityReportProps> = ({ report }) => {
  if (!report) {
    return (
      <Card title="质量报告" bordered={false}>
        <Empty description="暂无质量报告数据" />
      </Card>
    )
  }

  // Coverage chart options
  const coverageChartOption: EChartsOption = {
    title: {
      text: '需求覆盖度',
      left: 'center',
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}%',
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2,
        },
        label: {
          show: true,
          formatter: '{b}\n{c}%',
        },
        data: [
          {
            value: report.coverage_analysis.coverage_rate,
            name: '已覆盖',
            itemStyle: { color: '#52c41a' },
          },
          {
            value: 100 - report.coverage_analysis.coverage_rate,
            name: '未覆盖',
            itemStyle: { color: '#ff4d4f' },
          },
        ],
      },
    ],
  }

  // Quality score chart
  const scoreChartOption: EChartsOption = {
    title: {
      text: '质量评分',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    xAxis: {
      type: 'category',
      data: ['覆盖度', '质量分', '总分'],
    },
    yAxis: {
      type: 'value',
      max: 100,
    },
    series: [
      {
        type: 'bar',
        data: [
          {
            value: report.quality_score.coverage_score,
            itemStyle: { color: '#1890ff' },
          },
          {
            value: report.quality_score.quality_score,
            itemStyle: { color: '#52c41a' },
          },
          {
            value: report.quality_score.total_score,
            itemStyle: { color: '#faad14' },
          },
        ],
        label: {
          show: true,
          position: 'top',
          formatter: '{c}分',
        },
      },
    ],
  }

  const getScoreColor = (score: number): string => {
    if (score >= 90) return '#52c41a'
    if (score >= 70) return '#faad14'
    return '#ff4d4f'
  }

  const getScoreStatus = (score: number): string => {
    if (score >= 90) return '优秀'
    if (score >= 70) return '良好'
    return '需改进'
  }

  return (
    <Card title="质量报告" bordered={false}>
      {/* Score Overview */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="总体评分"
              value={report.quality_score.total_score}
              suffix="/ 100"
              valueStyle={{ color: getScoreColor(report.quality_score.total_score) }}
              prefix={<TrophyOutlined />}
            />
            <div style={{ marginTop: 8 }}>
              <Tag color={getScoreColor(report.quality_score.total_score)}>
                {getScoreStatus(report.quality_score.total_score)}
              </Tag>
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="覆盖度评分"
              value={report.quality_score.coverage_score}
              suffix="/ 100"
              valueStyle={{ color: getScoreColor(report.quality_score.coverage_score) }}
            />
            <Progress
              percent={report.quality_score.coverage_score}
              strokeColor={getScoreColor(report.quality_score.coverage_score)}
              showInfo={false}
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="质量评分"
              value={report.quality_score.quality_score}
              suffix="/ 100"
              valueStyle={{ color: getScoreColor(report.quality_score.quality_score) }}
            />
            <Progress
              percent={report.quality_score.quality_score}
              strokeColor={getScoreColor(report.quality_score.quality_score)}
              showInfo={false}
              style={{ marginTop: 8 }}
            />
          </Card>
        </Col>
      </Row>

      {/* Charts */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={12}>
          <Card>
            <ReactECharts option={coverageChartOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col span={12}>
          <Card>
            <ReactECharts option={scoreChartOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      {/* Coverage Analysis */}
      <Card title="覆盖度分析" size="small" style={{ marginBottom: 16 }}>
        <div style={{ marginBottom: 16 }}>
          <Progress
            percent={report.coverage_analysis.coverage_rate}
            status={report.coverage_analysis.coverage_rate >= 80 ? 'success' : 'normal'}
          />
        </div>
        {report.coverage_analysis.uncovered_points.length > 0 && (
          <Alert
            message="未覆盖的功能点"
            description={
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {report.coverage_analysis.uncovered_points.map((point, index) => (
                  <li key={index}>{point}</li>
                ))}
              </ul>
            }
            type="warning"
            icon={<WarningOutlined />}
            style={{ marginBottom: 16 }}
          />
        )}
        {report.coverage_analysis.missing_scenarios.length > 0 && (
          <Alert
            message="缺失的测试场景"
            description={
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {report.coverage_analysis.missing_scenarios.map((scenario, index) => (
                  <li key={index}>{scenario}</li>
                ))}
              </ul>
            }
            type="info"
            icon={<InfoCircleOutlined />}
          />
        )}
      </Card>

      {/* Quality Analysis */}
      <Card title="质量分析" size="small" style={{ marginBottom: 16 }}>
        {report.quality_analysis.duplicate_cases.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <Tag color="red">重复用例</Tag>
            <List
              size="small"
              dataSource={report.quality_analysis.duplicate_cases}
              renderItem={(item) => <List.Item>{item}</List.Item>}
            />
          </div>
        )}
        {report.quality_analysis.non_smart_cases.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <Tag color="orange">不符合SMART原则</Tag>
            <List
              size="small"
              dataSource={report.quality_analysis.non_smart_cases}
              renderItem={(item) => <List.Item>{item}</List.Item>}
            />
          </div>
        )}
        {report.quality_analysis.incomplete_data.length > 0 && (
          <div>
            <Tag color="blue">数据不完整</Tag>
            <List
              size="small"
              dataSource={report.quality_analysis.incomplete_data}
              renderItem={(item) => <List.Item>{item}</List.Item>}
            />
          </div>
        )}
      </Card>

      {/* Suggestions */}
      <Card title="改进建议" size="small">
        <List
          dataSource={report.suggestions}
          renderItem={(item) => (
            <List.Item>
              <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 8 }} />
              {item}
            </List.Item>
          )}
        />
      </Card>
    </Card>
  )
}

export default QualityReport
