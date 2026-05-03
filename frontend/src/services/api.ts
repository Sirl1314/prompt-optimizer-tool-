import axios from 'axios';
import type { ApiResponse, PipelineResult, HistoryItem, HistoryDetail, VersionItem, DomainStrategyData, DomainCreateRequest, ModelInfo, ModelCreateRequest } from '../types';

const http = axios.create({ baseURL: '/api', timeout: 120000 });

http.interceptors.response.use(
  (res) => res,
  (err) => {
    // 处理 422 验证错误
    if (err.response?.status === 422) {
      const detail = err.response.data?.detail;
      if (Array.isArray(detail)) {
        // Pydantic 验证错误
        const firstError = detail[0];
        const field = firstError.loc?.join('.') || '字段';
        const msg = firstError.msg || '验证失败';

        // 针对 prompt 字段的字数限制给出友好提示
        if (field.includes('prompt')) {
          if (msg.includes('greater than or equal to 10') || msg.includes('at least 10')) {
            return Promise.reject(new Error(`Prompt 字数不足，至少需要 10 个字符`));
          }
        }

        return Promise.reject(new Error(`优化失败：${field} - ${msg}`));
      }
    }

    const msg = err.response?.data?.message || err.message || '请求失败';
    return Promise.reject(new Error(msg));
  }
);

export async function optimizePrompt(prompt: string, domain?: string, model?: string, language?: string): Promise<PipelineResult> {
  const { data } = await http.post<ApiResponse<PipelineResult>>('/optimize', { prompt, domain, model, language });
  if (data.code !== 0) throw new Error(data.message);
  return data.data!;
}

export async function estimateTokens(prompt: string): Promise<{ token_count: number; char_count: number }> {
  const { data } = await http.post<ApiResponse<{ token_count: number; char_count: number }>>('/token-estimate', { prompt });
  return data.data!;
}

export async function fetchHistory(page = 1, pageSize = 20, domain?: string, search?: string) {
  const { data } = await http.get<ApiResponse<{ items: HistoryItem[]; total: number; page: number; page_size: number }>>('/history', { params: { page, page_size: pageSize, domain, search } });
  return data.data!;
}

export async function fetchHistoryDetail(id: string): Promise<HistoryDetail> {
  const { data } = await http.get<ApiResponse<HistoryDetail>>(`/history/${id}`);
  return data.data!;
}

export async function deleteHistory(id: string): Promise<void> {
  await http.delete(`/history/${id}`);
}

export async function fetchVersions(id: string): Promise<VersionItem[]> {
  const { data } = await http.get<ApiResponse<VersionItem[]>>(`/history/${id}/versions`);
  return data.data!;
}

export async function compareVersions(versionIds: string[]) {
  const { data } = await http.post<ApiResponse<{ versions: unknown[]; comparisons: unknown[] }>>('/compare', { version_ids: versionIds });
  return data.data!;
}

export async function fetchDomains(): Promise<DomainStrategyData[]> {
  const { data } = await http.get<ApiResponse<DomainStrategyData[]>>('/domains');
  return data.data!;
}

export async function createDomain(body: DomainCreateRequest): Promise<DomainStrategyData> {
  const { data } = await http.post<ApiResponse<DomainStrategyData>>('/domains', body);
  if (data.code !== 0) throw new Error(data.message);
  return data.data!;
}

export async function updateDomain(id: number, body: DomainCreateRequest): Promise<void> {
  const { data } = await http.put<ApiResponse<null>>(`/domains/${id}`, body);
  if (data.code !== 0) throw new Error(data.message);
}

export async function deleteDomain(id: number): Promise<void> {
  const { data } = await http.delete<ApiResponse<null>>(`/domains/${id}`);
  if (data.code !== 0) throw new Error(data.message);
}

export async function fetchModels(): Promise<ModelInfo[]> {
  const { data } = await http.get<ApiResponse<ModelInfo[]>>('/models');
  return data.data!;
}

export async function createModel(body: ModelCreateRequest): Promise<ModelInfo> {
  const { data } = await http.post<ApiResponse<ModelInfo>>('/models', body);
  if (data.code !== 0) throw new Error(data.message);
  return data.data!;
}

export async function updateModel(id: number, body: ModelCreateRequest): Promise<void> {
  const { data } = await http.put<ApiResponse<null>>(`/models/${id}`, body);
  if (data.code !== 0) throw new Error(data.message);
}

export async function deleteModel(id: number): Promise<void> {
  const { data } = await http.delete<ApiResponse<null>>(`/models/${id}`);
  if (data.code !== 0) throw new Error(data.message);
}

export async function testModel(modelName: string): Promise<boolean> {
  const { data } = await http.post<ApiResponse<{ available: boolean }>>('/models/test', { model_name: modelName });
  return data.data?.available ?? false;
}
