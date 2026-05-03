import { Descriptions, Card, Row, Col, Statistic } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import type { PipelineResult } from '../types';
import { DOMAIN_LABELS } from '../types';
import ScoreRadar from './ScoreRadar';
import DiffViewer from './DiffViewer';
import TokenBadge from './TokenBadge';

interface OptimizationResultProps {
  result: PipelineResult;
}

export default function OptimizationResult({ result }: OptimizationResultProps) {
  const scoreColor = result.scores.total >= 80 ? '#3f8600' : result.scores.total >= 60 ? '#faad14' : '#cf1322';

  return (
    <div style={{ marginTop: 24 }}>
      <Card title="优化报告" style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="综合评分"
              value={result.scores.total}
              suffix="分"
              valueStyle={{ color: scoreColor }}
            />
          </Col>
          <Col span={6}>
            <Statistic title="检测领域" value={DOMAIN_LABELS[result.domain] || result.domain} />
          </Col>
          <Col span={6}>
            <Statistic
              title="Token 变化"
              value={Math.abs(result.token_saved)}
              prefix={result.token_saved > 0 ? <ArrowDownOutlined /> : <ArrowUpOutlined />}
              suffix={result.token_saved > 0 ? '节省' : '增加'}
              valueStyle={{ color: result.token_saved > 0 ? '#3f8600' : '#cf1322' }}
            />
          </Col>
          <Col span={6}>
            <Statistic title="使用模型" value={result.model_used} />
          </Col>
        </Row>
        <Row gutter={16} style={{ marginTop: 16 }}>
          <Col span={12}>
            <TokenBadge count={result.token_count_raw} label="优化前" />
          </Col>
          <Col span={12}>
            <TokenBadge count={result.token_count_optimized} label="优化后" />
          </Col>
        </Row>
      </Card>

      <Row gutter={16}>
        <Col span={12}>
          <Card title="评分详情">
            <ScoreRadar scores={result.scores} />
          </Card>
        </Col>
        <Col span={12}>
          <Card title="结构诊断">
            <Descriptions column={1} size="small">
              <Descriptions.Item label="角色定义">{result.analysis_report.has_role_definition ? '✓' : '✗ 缺失'}</Descriptions.Item>
              <Descriptions.Item label="输出规范">{result.analysis_report.has_output_spec ? '✓' : '✗ 缺失'}</Descriptions.Item>
              <Descriptions.Item label="背景上下文">{result.analysis_report.has_context ? '✓' : '✗ 缺失'}</Descriptions.Item>
              <Descriptions.Item label="约束条件">{result.analysis_report.has_constraints ? '✓' : '✗ 缺失'}</Descriptions.Item>
              <Descriptions.Item label="冗余标记">{result.analysis_report.redundancy_markers.length} 处</Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>
      </Row>

      <Card title="优化后 Prompt" style={{ marginTop: 16 }}>
        <pre style={{
          whiteSpace: 'pre-wrap',
          wordWrap: 'break-word',
          background: '#f5f5f5',
          padding: '16px',
          borderRadius: 8,
          margin: 0,
          fontFamily: 'monospace',
          fontSize: '14px',
          lineHeight: '1.6'
        }}>
          {result.optimized_text}
        </pre>
      </Card>

      <Card title="优化前后对比" style={{ marginTop: 16 }}>
        <DiffViewer diffHtml={result.diff_html} />
      </Card>
    </div>
  );
}
