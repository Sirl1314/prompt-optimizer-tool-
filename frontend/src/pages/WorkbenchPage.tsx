import { useState, useEffect } from 'react';
import { notification } from 'antd';
import PromptInput from '../components/PromptInput';
import OptimizationResult from '../components/OptimizationResult';
import { optimizePrompt, fetchModels } from '../services/api';
import type { PipelineResult, ModelInfo } from '../types';

export default function WorkbenchPage() {
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState<ModelInfo[]>([]);

  useEffect(() => {
    fetchModels().then(setModels).catch(() => {});
  }, []);

  const handleSubmit = async (values: { prompt: string; domain?: string; model?: string; language?: string }) => {
    setLoading(true);
    try {
      const data = await optimizePrompt(values.prompt, values.domain, values.model, values.language);
      setResult(data);
    } catch (err: unknown) {
      notification.error({ message: '优化失败', description: (err as Error).message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PromptInput onSubmit={handleSubmit} loading={loading} models={models} />
      {result && <OptimizationResult result={result} />}
    </div>
  );
}
