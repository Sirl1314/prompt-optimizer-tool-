import { Tag } from 'antd';

interface TokenBadgeProps {
  count: number;
  label?: string;
}

export default function TokenBadge({ count, label }: TokenBadgeProps) {
  const color = count < 200 ? 'green' : count < 500 ? 'orange' : 'red';
  return <Tag color={color}>{label ? `${label}: ` : ''}{count} Token</Tag>;
}
