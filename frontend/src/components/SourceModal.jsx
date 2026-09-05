import { X, FileText } from "lucide-react";

export default function SourceModal({ source, onClose }) {
  if (!source) return null;
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="w-full max-w-lg rounded-xl border p-6"
        style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-2">
            <FileText size={18} style={{ color: "var(--accent)" }} />
            <div>
              <div className="font-medium text-sm">{source.source}</div>
              <div className="text-xs" style={{ color: "var(--muted)" }}>
                Retrieval match score: {source.rerank_score.toFixed(2)}
              </div>
            </div>
          </div>
          <button onClick={onClose}><X size={18} /></button>
        </div>

        <div
          className="text-sm leading-relaxed rounded-lg border p-3 whitespace-pre-wrap font-mono-plex"
          style={{ background: "var(--surface)", borderColor: "var(--surface-border)" }}
        >
          {source.snippet}
        </div>

        <div className="text-xs mt-3" style={{ color: "var(--muted)" }}>
          This is the exact text retrieved from the source document and given to the assistant —
          compare it against the answer above to verify grounding.
        </div>
      </div>
    </div>
  );
}