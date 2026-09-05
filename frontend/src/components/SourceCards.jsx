import { FileText } from "lucide-react";

export default function SourceCards({ sources, onSourceClick }) {
  if (!sources?.length) return null;
  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {sources.map((s, i) => (
        <button
          key={i}
          onClick={() => onSourceClick?.(s)}
          className="flex items-center gap-2 rounded-xl border px-3 py-2 text-xs shadow-sm text-left transition-colors hover:border-[var(--accent)]"
          style={{ background: "var(--surface)", borderColor: "var(--surface-border)" }}
        >
          <FileText size={16} style={{ color: "var(--accent)" }} />
          <div>
            <div className="font-medium">{s.source}</div>
            <div style={{ color: "var(--muted)" }}>Match {s.rerank_score.toFixed(2)} · Click to view</div>
          </div>
        </button>
      ))}
    </div>
  );
}