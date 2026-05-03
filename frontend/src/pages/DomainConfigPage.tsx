import { useState, useEffect, useCallback } from 'react';
import {
  Tabs, Card, Descriptions, Tag, List, Typography, Spin, Button, Modal,
  Form, Input, Select, InputNumber, Space, Divider, Popconfirm, message, Empty,
} from 'antd';
import { PlusOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { fetchDomains, createDomain, updateDomain, deleteDomain } from '../services/api';
import type { DomainStrategyData, DomainCreateRequest } from '../types';
import { DOMAIN_LABELS } from '../types';

const { Text } = Typography;
const { TextArea } = Input;

const DIMENSION_LABELS: Record<string, string> = {
  clarity: '清晰度',
  structure: '结构完整度',
  redundancy: '冗余控制',
  role_setting: '角色设定',
  output_spec: '输出规范',
};

const SEVERITY_LABELS: Record<string, string> = {
  critical: '严重',
  high: '高',
  medium: '中',
  low: '低',
};

const SEVERITY_COLORS: Record<string, string> = {
  critical: 'red',
  high: 'orange',
  medium: 'gold',
  low: 'default',
};

const DEFAULT_TEMPLATE: Record<string, string> = {
  '【精准角色定义】': '你是一位...',
  '【明确任务边界】': '核心任务：...',
};

const DEFAULT_RULES: Record<string, unknown>[] = [
  {
    name: '缺少角色定义',
    check_type: 'missing_keyword',
    keywords: ['角色', '你是一位'],
    severity: 'critical',
    fix_suggestion: '请在开头明确 AI 的角色定位',
  },
];

const DEFAULT_WEIGHTS: Record<string, number> = {
  clarity: 0.2,
  structure: 0.2,
  redundancy: 0.2,
  role_setting: 0.2,
  output_spec: 0.2,
};

function WeightSumText() {
  const weights = Form.useWatch('scoring_weights') as Record<string, number> | undefined;
  const total = weights
    ? Object.values(weights).reduce((a, b) => a + b, 0)
    : 0;
  const color = Math.abs(total - 1.0) < 0.01 ? 'green' : 'red';
  return (
    <Text type="secondary" style={{ display: 'block', marginBottom: 4 }}>
      当前权重合计：
      <Text strong style={{ color }}>{(total * 100).toFixed(0)}%</Text>
      {Math.abs(total - 1.0) >= 0.01 && (
        <Text type="danger">（五项权重之和必须为 1.0）</Text>
      )}
    </Text>
  );
}

export default function DomainConfigPage() {
  const [domains, setDomains] = useState<DomainStrategyData[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingDomain, setEditingDomain] = useState<DomainStrategyData | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  const loadDomains = useCallback(() => {
    setLoading(true);
    fetchDomains()
      .then(setDomains)
      .catch(() => message.error('加载领域配置失败'))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadDomains(); }, [loadDomains]);

  const openCreateModal = () => {
    setEditingDomain(null);
    form.resetFields();
    form.setFieldsValue({
      templateEntries: Object.entries(DEFAULT_TEMPLATE),
      rules: DEFAULT_RULES,
      scoring_weights: DEFAULT_WEIGHTS,
    });
    setModalOpen(true);
  };

  const openEditModal = (domain: DomainStrategyData) => {
    setEditingDomain(domain);
    form.setFieldsValue({
      domain_name: domain.domain_name,
      display_name: domain.display_name,
      templateEntries: Object.entries(domain.template),
      role_instruction: domain.role_instruction,
      rules: domain.rules,
      scoring_weights: domain.scoring_weights,
    });
    setModalOpen(true);
  };

  const handleDelete = async (domain: DomainStrategyData) => {
    try {
      await deleteDomain(domain.id);
      message.success('已删除');
      loadDomains();
    } catch (e) {
      message.error((e as Error).message);
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);

      const template: Record<string, string> = {};
      (values.templateEntries as [string, string][]).forEach(([k, v]) => {
        if (k.trim()) template[k.trim()] = v;
      });

      const body: DomainCreateRequest = {
        domain_name: values.domain_name,
        display_name: values.display_name,
        template,
        role_instruction: values.role_instruction,
        rules: values.rules as Record<string, unknown>[],
        scoring_weights: values.scoring_weights,
      };

      if (editingDomain) {
        await updateDomain(editingDomain.id, body);
        message.success('更新成功');
      } else {
        await createDomain(body);
        message.success('创建成功');
      }
      setModalOpen(false);
      loadDomains();
    } catch (e) {
      if ((e as Error).message) message.error((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <Spin style={{ display: 'block', marginTop: 48 }} />;

  const renderDomainContent = (d: DomainStrategyData) => (
    <div>
      <Card title="结构模板" style={{ marginBottom: 16 }}>
        {Object.entries(d.template).map(([section, desc]) => (
          <div key={section} style={{ marginBottom: 16 }}>
            <Tag color="blue" style={{ marginBottom: 8 }}>{section}</Tag>
            <pre style={{
              whiteSpace: 'pre-wrap', wordWrap: 'break-word',
              background: '#fafafa', padding: '12px 16px', borderRadius: 6,
              margin: 0, fontFamily: 'monospace', fontSize: '14px', lineHeight: '1.6',
            }}>
              {desc}
            </pre>
          </div>
        ))}
      </Card>

      <Card title="角色指令" style={{ marginBottom: 16 }}>
        <pre style={{
          whiteSpace: 'pre-wrap', wordWrap: 'break-word',
          background: '#fafafa', padding: '12px 16px', borderRadius: 6,
          margin: 0, fontFamily: 'monospace', fontSize: '14px', lineHeight: '1.6',
        }}>
          {d.role_instruction}
        </pre>
      </Card>

      <Card title="优化规则" style={{ marginBottom: 16 }}>
        <List
          dataSource={d.rules}
          renderItem={(rule: Record<string, unknown>) => (
            <List.Item>
              <List.Item.Meta
                title={
                  <span>
                    {rule.name as string}{' '}
                    <Tag color={SEVERITY_COLORS[rule.severity as string] || 'default'}>
                      {SEVERITY_LABELS[rule.severity as string] || (rule.severity as string)}
                    </Tag>
                  </span>
                }
                description={rule.fix_suggestion as string}
              />
            </List.Item>
          )}
        />
      </Card>

      <Card title="评分权重">
        <Descriptions bordered size="small">
          {Object.entries(d.scoring_weights).map(([dim, weight]) => (
            <Descriptions.Item key={dim} label={DIMENSION_LABELS[dim] || dim}>
              <Text strong>{(weight as number * 100).toFixed(0)}%</Text>
            </Descriptions.Item>
          ))}
        </Descriptions>
        <Text type="secondary" style={{ display: 'block', marginTop: 8 }}>
          合计：{(Object.values(d.scoring_weights).reduce((a, b) => a + b, 0) * 100).toFixed(0)}%
        </Text>
      </Card>
    </div>
  );

  const tabItems = domains.map((d) => ({
    key: String(d.id),
    label: (
      <span>
        {d.is_custom ? d.display_name : (DOMAIN_LABELS[d.domain_name] || d.display_name || d.domain_name)}
        {d.is_custom && <Tag color="orange" style={{ marginLeft: 6, fontSize: 10 }}>自定义</Tag>}
      </span>
    ),
    children: (
      <div>
        {d.is_custom && (
          <div style={{ marginBottom: 12, display: 'flex', gap: 8 }}>
            <Button size="small" icon={<EditOutlined />} onClick={() => openEditModal(d)}>
              编辑
            </Button>
            <Popconfirm
              title="确定删除该自定义领域？"
              description="删除后不可恢复，使用该领域的记录将回退到通用策略。"
              onConfirm={() => handleDelete(d)}
              okText="确定"
              cancelText="取消"
            >
              <Button size="small" danger icon={<DeleteOutlined />}>删除</Button>
            </Popconfirm>
          </div>
        )}
        {renderDomainContent(d)}
      </div>
    ),
  }));

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Text strong style={{ fontSize: 16 }}>领域策略配置</Text>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreateModal}>
          添加自定义领域
        </Button>
      </div>

      {domains.length === 0 ? (
        <Empty description="暂无领域配置" />
      ) : (
        <Tabs items={tabItems} />
      )}

      <Modal
        title={editingDomain ? '编辑自定义领域' : '添加自定义领域'}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        confirmLoading={submitting}
        width={900}
        destroyOnClose
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Space style={{ width: '100%' }} size={16}>
            <Form.Item
              name="domain_name"
              label="领域标识"
              rules={[
                { required: true, message: '请输入领域标识' },
                { pattern: /^[a-z0-9_]+$/, message: '只能包含小写字母、数字和下划线' },
              ]}
              style={{ width: 240 }}
            >
              <Input placeholder="例如: game_dev" disabled={!!editingDomain} />
            </Form.Item>
            <Form.Item
              name="display_name"
              label="显示名称"
              rules={[{ required: true, message: '请输入显示名称' }]}
              style={{ width: 240 }}
            >
              <Input placeholder="例如: 游戏开发" />
            </Form.Item>
          </Space>

          <Divider>结构模板</Divider>
          <Form.List name="templateEntries">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...rest }) => (
                  <Space key={key} style={{ display: 'flex', marginBottom: 8 }} align="baseline">
                    <Form.Item {...rest} name={[name, 0]} rules={[{ required: true, message: '章节名' }]}>
                      <Input placeholder="章节名称，如：【精准角色定义】" style={{ width: 260 }} />
                    </Form.Item>
                    <Form.Item {...rest} name={[name, 1]} rules={[{ required: true, message: '模板内容' }]}>
                      <TextArea placeholder="模板内容，用 {placeholder} 表示占位符" rows={2} style={{ width: 440 }} />
                    </Form.Item>
                    <Button onClick={() => remove(name)} icon={<DeleteOutlined />} danger size="small" />
                  </Space>
                ))}
                <Button type="dashed" onClick={() => add(['', ''])} block icon={<PlusOutlined />}>
                  添加模板章节
                </Button>
              </>
            )}
          </Form.List>

          <Divider>角色指令</Divider>
          <Form.Item
            name="role_instruction"
            rules={[{ required: true, message: '请输入角色指令' }]}
          >
            <TextArea placeholder="描述 AI 在该领域应扮演的角色和遵循的原则" rows={4} />
          </Form.Item>

          <Divider>优化规则</Divider>
          <Form.List name="rules">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...rest }) => (
                  <Card
                    key={key}
                    size="small"
                    style={{ marginBottom: 12 }}
                    extra={<Button onClick={() => remove(name)} icon={<DeleteOutlined />} danger size="small" />}
                    title={
                      <Form.Item {...rest} name={[name, 'name']} rules={[{ required: true, message: '规则名称' }]} noStyle>
                        <Input placeholder="规则名称" style={{ width: 300 }} />
                      </Form.Item>
                    }
                  >
                    <Space wrap>
                      <Form.Item {...rest} name={[name, 'check_type']} rules={[{ required: true }]} style={{ marginBottom: 0 }}>
                        <Select style={{ width: 180 }} options={[
                          { value: 'missing_keyword', label: '缺少关键词' },
                          { value: 'pattern_violation', label: '模式匹配' },
                          { value: 'missing_template_section', label: '缺少模板章节' },
                        ]} />
                      </Form.Item>
                      <Form.Item {...rest} name={[name, 'severity']} rules={[{ required: true }]} style={{ marginBottom: 0 }}>
                        <Select style={{ width: 100 }} options={[
                          { value: 'critical', label: '严重' },
                          { value: 'high', label: '高' },
                          { value: 'medium', label: '中' },
                          { value: 'low', label: '低' },
                        ]} />
                      </Form.Item>
                    </Space>
                    <Form.Item {...rest} name={[name, 'keywords']} style={{ marginBottom: 8, marginTop: 8 }}>
                      <Select mode="tags" placeholder="关键词（用于 missing_keyword 检查）" style={{ width: '100%' }} />
                    </Form.Item>
                    <Form.Item {...rest} name={[name, 'fix_suggestion']} rules={[{ required: true, message: '修复建议' }]} style={{ marginBottom: 0 }}>
                      <Input placeholder="修复建议" />
                    </Form.Item>
                  </Card>
                ))}
                <Button type="dashed" onClick={() => add({
                  name: '', check_type: 'missing_keyword', keywords: [],
                  severity: 'medium', fix_suggestion: '',
                })} block icon={<PlusOutlined />}>
                  添加规则
                </Button>
              </>
            )}
          </Form.List>

          <Divider>评分权重</Divider>
          <WeightSumText />
          <Space wrap>
            {Object.keys(DEFAULT_WEIGHTS).map((dim) => (
              <Form.Item
                key={dim}
                name={['scoring_weights', dim]}
                label={DIMENSION_LABELS[dim] || dim}
                rules={[{ required: true, message: '必填' }]}
              >
                <InputNumber min={0} max={1} step={0.05} style={{ width: 120 }} placeholder="0.20" />
              </Form.Item>
            ))}
          </Space>
        </Form>
      </Modal>
    </div>
  );
}
