export interface ScoreDetail {
  score: number;
  weight: number;
  notes: string;
}

export interface ScoreReport {
  clarity: ScoreDetail;
  structure: ScoreDetail;
  redundancy: ScoreDetail;
  role_setting: ScoreDetail;
  output_spec: ScoreDetail;
  total: number;
}

export interface RedundancyMarker {
  text_segment: string;
  reason: string;
  suggestion: string;
}

export interface AnalysisReport {
  has_role_definition: boolean;
  has_output_spec: boolean;
  has_context: boolean;
  has_constraints: boolean;
  structure_score: number;
  redundancy_markers: RedundancyMarker[];
  missing_sections: string[];
}

export interface PipelineResult {
  original_text: string;
  optimized_text: string;
  domain: string;
  domain_confidence: number;
  scores: ScoreReport;
  token_count_raw: number;
  token_count_optimized: number;
  token_saved: number;
  diff_html: string;
  model_used: string;
  analysis_report: AnalysisReport;
}

export interface HistoryItem {
  id: string;
  title: string;
  domain: string;
  token_count_raw: number;
  token_count_optimized: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface VersionItem {
  id: string;
  version: number;
  optimized_text: string;
  model_used: string;
  domain_strategy: string;
  scores: ScoreReport | null;
  diff_html: string | null;
  token_delta: number;
  created_at: string;
}

export interface HistoryDetail extends HistoryItem {
  raw_prompt: string;
  optimized_prompt: string | null;
  source_model: string | null;
  versions: VersionItem[];
}

export interface DomainStrategyData {
  id: number;
  domain_name: string;
  display_name: string;
  template: Record<string, string>;
  role_instruction: string;
  rules: Record<string, unknown>[];
  scoring_weights: Record<string, number>;
  is_active: boolean;
  version: number;
  is_custom: boolean;
}

export interface DomainCreateRequest {
  domain_name: string;
  display_name: string;
  template: Record<string, string>;
  role_instruction: string;
  rules: Record<string, unknown>[];
  scoring_weights: Record<string, number>;
}

export interface ModelInfo {
  id: number;
  model_name: string;
  provider: string;
  api_endpoint?: string;
  max_tokens?: number;
  temperature?: number;
  is_available?: boolean;
  is_custom: boolean;
}

export interface ModelCreateRequest {
  model_name: string;
  provider: string;
  api_endpoint: string;
  api_key: string;
  max_tokens: number;
  temperature: number;
}

export interface ApiResponse<T = unknown> {
  code: number;
  data: T;
  message: string;
}

export const DOMAIN_LABELS: Record<string, string> = {
  code_dev: '代码开发',
  copywriting: '文案写作',
  data_analysis: '数据分析',
  marketing: '市场营销',
  healthcare: '医疗健康',
  legal: '法律',
  education: '教育',
  ai_visual: 'AI 视觉',
};
