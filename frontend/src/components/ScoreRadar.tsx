import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import type { ScoreReport } from '../types';

interface ScoreRadarProps {
  scores: ScoreReport;
}

export default function ScoreRadar({ scores }: ScoreRadarProps) {
  const data = [
    { name: '清晰度', value: scores.clarity.score },
    { name: '结构', value: scores.structure.score },
    { name: '冗余度', value: scores.redundancy.score },
    { name: '角色', value: scores.role_setting.score },
    { name: '输出规范', value: scores.output_spec.score },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data}>
        <PolarGrid />
        <PolarAngleAxis dataKey="name" />
        <PolarRadiusAxis angle={30} domain={[0, 100]} />
        <Radar name="评分" dataKey="value" stroke="#1677ff" fill="#1677ff" fillOpacity={0.3} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
