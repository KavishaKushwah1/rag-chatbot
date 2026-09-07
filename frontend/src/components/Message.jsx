import { FileText } from "lucide-react";
import SourceCards from "./SourceCards";

/**
 * Escapes HTML first (XSS-safe), then converts a small, safe subset of
 * markdown (bold, line breaks) to real HTML. Gemini's output regularly
 * uses **bold** for emphasis — without this, users see literal asterisks.
 */
function formatContent(raw) {
  const escaped = raw
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  return escaped
    .replace(/\*\*\*(.+?)\*\*\*/g, "<strong><em>$1</em></strong>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/^\* (.+)$/gm, "• $1")
    .replace(/\n/g, "<br>");
}

export default function Message({ role, content, ts, sources, usedAttachments, streaming, onSourceClick }) {
  if (role === "user") {
    return (
      <div className="flex justify-end items-start gap-2 my-3">
        <span className="text-xs whitespace-nowrap pt-2" style={{ color: "var(--muted)" }}>{ts}</span>
        <div
          className="rounded-2xl px-4 py-2 text-sm max-w-[60vw]"
          style={{ background: "var(--user-bubble-bg)", color: "var(--user-bubble-text)" }}
        >
          {content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-2 my-3">
      <div
        className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
        style={{ background: "var(--accent-soft)" }}
      >
        <FileText size={16} style={{ color: "var(--accent)" }} />
      </div>
      <div className="max-w-[78%]">
        <div
          className="text-sm leading-relaxed"
          dangerouslySetInnerHTML={{ __html: formatContent(content) }}
        />
        {streaming && <span className="animate-pulse text-sm">▌</span>}
        <SourceCards sources={sources} onSourceClick={onSourceClick} />
        {usedAttachments?.length > 0 && (
          <div className="text-xs mt-2" style={{ color: "var(--muted)" }}>
            📎 Answered using: {usedAttachments.join(", ")}
          </div>
        )}
      </div>
      <span className="text-xs whitespace-nowrap pt-2" style={{ color: "var(--muted)" }}>{ts}</span>
    </div>
  );
}