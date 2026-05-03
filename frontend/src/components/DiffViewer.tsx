interface DiffViewerProps {
  diffHtml: string;
}

export default function DiffViewer({ diffHtml }: DiffViewerProps) {
  return (
    <div
      style={{ maxHeight: 500, overflow: 'auto', fontSize: 13 }}
      dangerouslySetInnerHTML={{ __html: diffHtml }}
    />
  );
}
