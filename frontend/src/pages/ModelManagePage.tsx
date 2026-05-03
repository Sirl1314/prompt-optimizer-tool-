import { useState, useEffect, useCallback } from 'react';
import {
  Card, Button, Tag, Row, Col, Spin, Modal, Form, Input, InputNumber,
  Select, Popconfirm, notification, Typography, Empty, message,
} from 'antd';
import {
  ApiOutlined, CheckCircleOutlined, CloseCircleOutlined,
  PlusOutlined, EditOutlined, DeleteOutlined,
} from '@ant-design/icons';
import { fetchModels, createModel, updateModel, deleteModel, testModel } from '../services/api';
import type { ModelInfo, ModelCreateRequest } from '../types';

const { Text } = Typography;

const providerColors: Record<string, string> = {
  deepseek: 'blue', openai: 'green', qwen: 'purple',
  xiaomi_mimo: 'orange',
};

const PROVIDER_PRESETS = [
  { label: 'DeepSeek', value: 'deepseek' },
  { label: 'OpenAI', value: 'openai' },
  { label: 'Qwen / 通义千问', value: 'qwen' },
  { label: 'Xiaomi MiMo', value: 'xiaomi_mimo' },
  { label: 'SiliconFlow / 硅基流动', value: 'siliconflow' },
  { label: 'Groq', value: 'groq' },
  { label: 'Together AI', value: 'together' },
  { label: 'Ollama (本地)', value: 'ollama' },
  { label: '其他 / 自定义', value: 'custom' },
];

export default function ModelManagePage() {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState<string | null>(null);
  const [statuses, setStatuses] = useState<Record<string, boolean | null>>({});

  const [modalOpen, setModalOpen] = useState(false);
  const [editingModel, setEditingModel] = useState<ModelInfo | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form] = Form.useForm();

  const loadModels = useCallback(() => {
    setLoading(true);
    fetchModels()
      .then(setModels)
      .catch(() => notification.error({ message: '加载模型列表失败' }))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => { loadModels(); }, [loadModels]);

  const handleTest = async (modelName: string) => {
    setTesting(modelName);
    try {
      const ok = await testModel(modelName);
      setStatuses((prev) => ({ ...prev, [modelName]: ok }));
      message.success(ok ? '连接成功' : '连接失败');
    } catch {
      setStatuses((prev) => ({ ...prev, [modelName]: false }));
      message.error('测试失败');
    } finally {
      setTesting(null);
    }
  };

  const openCreateModal = () => {
    setEditingModel(null);
    form.resetFields();
    form.setFieldsValue({
      max_tokens: 4096,
      temperature: 0.7,
    });
    setModalOpen(true);
  };

  const openEditModal = (model: ModelInfo) => {
    setEditingModel(model);
    form.setFieldsValue({
      model_name: model.model_name,
      provider: model.provider,
      api_endpoint: model.api_endpoint || '',
      api_key: '',
      max_tokens: model.max_tokens || 4096,
      temperature: model.temperature || 0.7,
    });
    setModalOpen(true);
  };

  const handleDelete = async (model: ModelInfo) => {
    try {
      await deleteModel(model.id);
      message.success('已删除');
      loadModels();
    } catch (e) {
      message.error((e as Error).message);
    }
  };

  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);

      // 处理 provider 字段：如果是数组则取第一个元素
      const providerValue = Array.isArray(values.provider)
        ? values.provider[0]
        : values.provider;

      const body: ModelCreateRequest = {
        model_name: values.model_name,
        provider: providerValue,
        api_endpoint: values.api_endpoint,
        api_key: values.api_key,
        max_tokens: values.max_tokens,
        temperature: values.temperature,
      };

      if (editingModel) {
        await updateModel(editingModel.id, body);
        message.success('更新成功');
      } else {
        await createModel(body);
        message.success('创建成功');
      }
      setModalOpen(false);
      loadModels();
    } catch (e) {
      if ((e as Error).message) message.error((e as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  const getProviderColor = (provider: string) => {
    return providerColors[provider] || 'default';
  };

  if (loading) return <Spin style={{ display: 'block', marginTop: 48 }} />;

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Text strong style={{ fontSize: 16 }}>模型管理</Text>
        <Button type="primary" icon={<PlusOutlined />} onClick={openCreateModal}>
          添加自定义模型
        </Button>
      </div>

      {models.length === 0 ? (
        <Empty description="暂无模型，请设置环境变量或添加自定义模型" />
      ) : (
        <Row gutter={[16, 16]}>
          {models.map((model) => (
            <Col key={model.model_name} xs={24} sm={12} lg={8}>
              <Card
                title={
                  <span>
                    <ApiOutlined style={{ marginRight: 8 }} />
                    {model.model_name}
                    {model.is_custom && <Tag color="orange" style={{ marginLeft: 8, fontSize: 10 }}>自定义</Tag>}
                  </span>
                }
                extra={<Tag color={getProviderColor(model.provider)}>{model.provider}</Tag>}
              >
                <div style={{ marginBottom: 12 }}>
                  <Text type="secondary">提供商：{model.provider}</Text>
                </div>
                <div style={{ marginBottom: 12 }}>
                  状态：{' '}
                  {statuses[model.model_name] === true ? (
                    <Tag icon={<CheckCircleOutlined />} color="success">已连接</Tag>
                  ) : statuses[model.model_name] === false ? (
                    <Tag icon={<CloseCircleOutlined />} color="error">连接失败</Tag>
                  ) : (
                    <Tag>未测试</Tag>
                  )}
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <Button
                    onClick={() => handleTest(model.model_name)}
                    loading={testing === model.model_name}
                  >
                    测试连接
                  </Button>
                  {model.is_custom && (
                    <>
                      <Button size="small" icon={<EditOutlined />} onClick={() => openEditModal(model)}>
                        编辑
                      </Button>
                      <Popconfirm
                        title="确定删除该模型？"
                        onConfirm={() => handleDelete(model)}
                        okText="确定"
                        cancelText="取消"
                      >
                        <Button size="small" danger icon={<DeleteOutlined />} />
                      </Popconfirm>
                    </>
                  )}
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      )}

      <Modal
        title={editingModel ? '编辑自定义模型' : '添加自定义模型'}
        open={modalOpen}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        confirmLoading={submitting}
        width={560}
        destroyOnClose
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item
            name="model_name"
            label="模型名称"
            rules={[{ required: true, message: '请输入模型名称' }]}
          >
            <Input placeholder="例如: gpt-4o-mini 或 qwen2.5-7b" disabled={!!editingModel} />
          </Form.Item>

          <Form.Item
            name="provider"
            label="提供商"
            rules={[{ required: true, message: '请选择或输入提供商' }]}
          >
            <Select
              placeholder="选择或输入提供商"
              options={PROVIDER_PRESETS}
              showSearch
              optionFilterProp="label"
            />
          </Form.Item>

          <Form.Item
            name="api_endpoint"
            label="API 端点"
            rules={[
              { required: true, message: '请输入 API 端点' },
              { type: 'url', message: '请输入有效的 URL' },
            ]}
          >
            <Input placeholder="https://api.openai.com/v1" />
          </Form.Item>

          <Form.Item
            name="api_key"
            label="API 密钥"
            rules={editingModel ? [] : [{ required: true, message: '请输入 API 密钥' }]}
            extra={editingModel ? '留空则不修改已有密钥' : undefined}
          >
            <Input.Password placeholder="sk-..." />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="max_tokens" label="最大 Token 数">
                <InputNumber min={256} max={131072} step={256} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="temperature"
                label="Temperature"
                rules={[
                  { type: 'number', min: 0, max: 2, message: '范围 0-2' },
                ]}
              >
                <InputNumber min={0} max={2} step={0.1} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
}
