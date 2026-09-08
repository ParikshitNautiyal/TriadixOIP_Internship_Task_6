export default function SourceList({ sources }) {
  if (!sources || sources.length === 0) return null;
  return (
    <div className="source-list">
      <span className="source-label">Sources</span>
      <ul>
        {sources.map((s, i) => (
          <li key={i} className="source-chip">
            <span className="mono">[{i + 1}]</span> {s.doc_name} — {s.unit_label} {s.page_number}
          </li>
        ))}
      </ul>
    </div>
  );
}
