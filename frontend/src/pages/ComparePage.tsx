import { useState, useEffect } from 'react';
import { Select, Button, Card, Space, notification, Empty, Spin } from 'antd';
import { SwapOutlined } from '@ant-design/icons';
import { fetchHistory, fetchVersions, compareVersions } from '../services/api';
import type { HistoryItem, VersionItem } from '../types';
import DiffViewer from '../components/DiffViewer';

export default function ComparePage() {
  const [records, setRecords] = useState<HistoryItem[]>([]);
  const [versions, setVersions] = useState<VersionItem[]>([]);
  const [selectedRecord, setSelectedRecord] = useState<string>();
  const [selectedVersions, setSelectedVersions] = useState<string[]>([]);
  const [comparisons, setComparisons] = useState<{ version_a: number; version_b: number; diff_html: string }[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHistory(1, 100).then((res) => setRecords(res.items)).catch(() => {});
  }, []);

  const handleRecordChange = async (recordId: string) => {
    setSelectedRecord(recordId);
    setSelectedVersions([]);
    setComparisons([]);
    try {
      const v = await fetchVersions(recordId);
      setVersions(v);
    } catch { notification.error({ message: '加载版本失败' }); }
  };

  const handleCompare = async () => {
    if (selectedVersions.length < 2) return;
    setLoading(true);
    try {
      const res = await compareVersions(selectedVersions);
      setComparisons(res.comparisons as { version_a: number; version_b: number; diff_html: string }[]);
    } catch { notification.error({ message: '对比失败' }); }
    finally { setLoading(false); }
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Select
          placeholder="选择记录"
          style={{ width: 300 }}
          value={selectedRecord}
          onChange={handleRecordChange}
          showSearch
          filterOption={(input, option) => (option?.label as string || '').toLowerCase().includes(input.toLowerCase())}
          options={records.map((r) => ({ value: r.id, label: r.title }))}
        />
        <Select
          mode="multiple"
          placeholder="选择 2-5 个版本"
          style={{ width: 400 }}
          value={selectedVersions}
          onChange={setSelectedVersions}
          maxCount={5}
          options={versions.map((v) => ({ value: v.id, label: `v${v.version} - ${v.model_used}` }))}
        />
        <Button
          type="primary"
          icon={<SwapOutlined />}
          onClick={handleCompare}
          loading={loading}
          disabled={selectedVersions.length < 2}
        >
          对比
        </Button>
      </Space>

      {comparisons.length === 0 && !loading && <Empty description="选择版本进行对比" />}

      <Spin spinning={loading}>
        {comparisons.map((c, i) => (
          <Card key={i} title={`v${c.version_a} vs v${c.version_b}`} style={{ marginBottom: 16 }}>
            <DiffViewer diffHtml={c.diff_html} />
          </Card>
        ))}
      </Spin>
    </div>
  );
}
