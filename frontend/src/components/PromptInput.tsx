import { Input, Select, Button, Space, Form, message } from 'antd';
import { ThunderboltOutlined } from '@ant-design/icons';
import type { ModelInfo } from '../types';
import { DOMAIN_LABELS } from '../types';

const { TextArea } = Input;

interface PromptInputProps {
  onSubmit: (values: { prompt: string; domain?: string; model?: string; language?: string }) => void;
  loading: boolean;
  models: ModelInfo[];
}

export default function PromptInput({ onSubmit, loading, models }: PromptInputProps) {
  const [form] = Form.useForm();

  const handleFinishFailed = (errorInfo: any) => {
    const { errorFields } = errorInfo;
    if (errorFields.length > 0) {
      const firstError = errorFields[0];
      message.warning(firstError.errors[0]);
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={onSubmit}
      onFinishFailed={handleFinishFailed}
    >
      <Form.Item
        name="prompt"
        rules={[
          { required: true, message: '⚠️ 请输入需要优化的 Prompt' },
          { min: 2, message: '⚠️ Prompt 至少需要 2 个字符，当前输入过短' }
        ]}
      >
        <TextArea
          rows={6}
          placeholder="请输入原始 Prompt（建议至少 10 个字符以获得更好的优化效果）..."
          maxLength={20000}
          showCount
        />
      </Form.Item>
      <Space>
        <Form.Item name="domain" style={{ marginBottom: 0 }}>
          <Select
            placeholder="自动检测领域"
            allowClear
            style={{ width: 180 }}
            options={Object.entries(DOMAIN_LABELS).map(([k, v]) => ({ value: k, label: v }))}
          />
        </Form.Item>
        <Form.Item name="language" style={{ marginBottom: 0 }} initialValue="zh">
          <Select
            placeholder="输出语言"
            style={{ width: 140 }}
            options={[
              { value: 'zh', label: '中文输出' },
              { value: 'en', label: '英文输出' },
              { value: 'auto', label: '自动检测' },
            ]}
          />
        </Form.Item>
        <Form.Item name="model" style={{ marginBottom: 0 }}>
          <Select
            placeholder="选择模型"
            style={{ width: 200 }}
            options={models.map((m) => ({ value: m.model_name, label: `${m.provider} / ${m.model_name}` }))}
          />
        </Form.Item>
        <Form.Item style={{ marginBottom: 0 }}>
          <Button
            type="primary"
            htmlType="submit"
            icon={<ThunderboltOutlined />}
            loading={loading}
          >
            开始优化
          </Button>
        </Form.Item>
      </Space>
    </Form>
  );
}
