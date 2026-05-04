import { useState, useEffect } from 'react';
import { Table, Button, Input, Select, Space, Drawer, Card, Descriptions, Tag, Popconfirm, notification, Typography } from 'antd';
import { DeleteOutlined, EyeOutlined, SearchOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { fetchHistory, fetchHistoryDetail, deleteHistory } from '../services/api';
import type { HistoryItem, HistoryDetail } from '../types';
import { DOMAIN_LABELS } from '../types';
import TokenBadge from '../components/TokenBadge';
import dayjs from 'dayjs';

export default function HistoryPage() {
  const [data, setData] = useState<HistoryItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [domainFilter, setDomainFilter] = useState<string>();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [detail, setDetail] = useState<HistoryDetail | null>(null);

  const load = async (p = page) => {
    setLoading(true);
    try {
      const res = await fetchHistory(p, 20, domainFilter, search || undefined);
      setData(res.items);
      setTotal(res.total);
    } catch {
      notification.error({ message: '加载历史记录失败' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [page, domainFilter]);

  const handleView = async (id: string) => {
    try {
      const d = await fetchHistoryDetail(id);
      setDetail(d);
      setDrawerOpen(true);
    } catch {
      notification.error({ message: '加载详情失败' });
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteHistory(id);
      load();
    } catch {
      notification.error({ message: '删除失败' });
    }
  };

  const columns: ColumnsType<HistoryItem> = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (text: string, record: HistoryItem) => (
        <span>
          {text}
          <Tag style={{ marginLeft: 8 }}>v{record.version}</Tag>
        </span>
      ),
    },
    {
      title: '领域',
      dataIndex: 'domain',
      key: 'domain',
      width: 130,
      render: (d: string) => <Tag>{DOMAIN_LABELS[d] || d}</Tag>,
    },
    {
      title: '使用模型',
      dataIndex: 'model_used',
      key: 'model_used',
      width: 150,
      ellipsis: true,
      render: (model: string) => <Tag color="blue">{model}</Tag>,
    },
    {
      title: 'Token 数（优化前）',
      dataIndex: 'token_count_raw',
      key: 'tokens_raw',
      width: 110,
      render: (v: number) => <TokenBadge count={v} />,
    },
    {
      title: 'Token 数（优化后）',
      dataIndex: 'token_count_optimized',
      key: 'tokens_optimized',
      width: 110,
      render: (v: number) => <TokenBadge count={v} />,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (s: string) => {
        const labels: Record<string, string> = { draft: '草稿', optimized: '已优化', archived: '已归档' };
        return <Tag color={s === 'optimized' ? 'green' : s === 'archived' ? 'default' : 'blue'}>{labels[s] || s}</Tag>;
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 170,
      render: (t: string) => dayjs(t).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '操作',
      key: 'actions',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button size="small" icon={<EyeOutlined />} onClick={() => handleView(record.record_id)} />
          <Popconfirm title="确认删除？" onConfirm={() => handleDelete(record.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="搜索..."
          prefix={<SearchOutlined />}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onPressEnter={() => load(1)}
          style={{ width: 250 }}
        />
        <Select
          placeholder="筛选领域"
          allowClear
          style={{ width: 160 }}
          value={domainFilter}
          onChange={(v) => { setDomainFilter(v); setPage(1); }}
          options={Object.entries(DOMAIN_LABELS).map(([k, v]) => ({ value: k, label: v }))}
        />
      </Space>

      <Table
        columns={columns}
        dataSource={data}
        rowKey="id"
        loading={loading}
        pagination={{ current: page, total, pageSize: 20, onChange: (p) => setPage(p) }}
      />

      <Drawer
        title="记录详情"
        width={640}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      >
        {detail && (
          <>
            <Descriptions column={1} size="small" bordered style={{ marginBottom: 16 }}>
              <Descriptions.Item label="标题">{detail.title}</Descriptions.Item>
              <Descriptions.Item label="领域">{DOMAIN_LABELS[detail.domain] || detail.domain}</Descriptions.Item>
              <Descriptions.Item label="模型">{detail.source_model || '-'}</Descriptions.Item>
              <Descriptions.Item label="优化前 Token">{detail.token_count_raw}</Descriptions.Item>
              <Descriptions.Item label="优化后 Token">{detail.token_count_optimized}</Descriptions.Item>
              <Descriptions.Item label="状态">{({ draft: '草稿', optimized: '已优化', archived: '已归档' } as Record<string, string>)[detail.status] || detail.status}</Descriptions.Item>
            </Descriptions>
            <Typography.Title level={5}>原始 Prompt</Typography.Title>
            <pre style={{ whiteSpace: 'pre-wrap', background: '#f5f5f5', padding: 12, borderRadius: 4, maxHeight: 200, overflow: 'auto' }}>
              {detail.raw_prompt}
            </pre>
            {detail.optimized_prompt && (
              <>
                <Typography.Title level={5} style={{ marginTop: 16 }}>优化后 Prompt</Typography.Title>
                <pre style={{ whiteSpace: 'pre-wrap', background: '#f0fff0', padding: 12, borderRadius: 4, maxHeight: 200, overflow: 'auto' }}>
                  {detail.optimized_prompt}
                </pre>
              </>
            )}
            <Typography.Title level={5} style={{ marginTop: 16 }}>版本列表（{detail.versions.length}）</Typography.Title>
            {detail.versions.map((v) => (
              <Card key={v.id} size="small" style={{ marginBottom: 8 }} title={`v${v.version} - ${v.model_used}`}>
                <p>Token 变化：{v.token_delta}</p>
                {v.scores && <p>评分：{(v.scores as { total: number }).total}</p>}
                {v.optimized_text && (
                  <>
                    <Typography.Text type="secondary">优化后 Prompt：</Typography.Text>
                    <pre style={{ whiteSpace: 'pre-wrap', background: '#f0fff0', padding: 12, borderRadius: 4, maxHeight: 200, overflow: 'auto', marginTop: 8 }}>
                      {v.optimized_text}
                    </pre>
                  </>
                )}
              </Card>
            ))}
          </>
        )}
      </Drawer>
    </div>
  );
}
