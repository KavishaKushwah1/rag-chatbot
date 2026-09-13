import { useState } from "react";
import { FileText, Copy, Pencil, RotateCcw, Check, ThumbsUp, ThumbsDown } from "lucide-react";
import SourceCards from "./SourceCards";

export function formatContent(raw) {
  const escaped = raw
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  return escaped
    .replace(/(?<!^)(?<!\n)(\d+\.\s+\*\*)/g, "\n$1")
    .replace(/\*\*\*(.+?)\*\*\*/g, "<strong><em>$1</em></strong>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/^\* (.+)$/gm, "• $1")
    .replace(/\n/g, "<br>");
}

export default function Message({
  role, content, ts, sources, streaming, onSourceClick,
  messageId, token, isLastUser, onEdit, onRegenerate,
}) {
  const [feedback, setFeedback] = useState(null);
  const [feedbackStatus, setFeedbackStatus] = useState(null);
  const [copied, setCopied] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editValue, setEditValue] = useState(content);

  async function sendFeedback(rating) {
    if (!messageId) return;
    setFeedbackStatus("saving");
    try {
      const { submitFeedback } = await import("../api");
      const ok = await submitFeedback(token, messageId, rating);
      if (ok) {
        setFeedback(rating);
        setFeedbackStatus("saved");
        setTimeout(() => setFeedbackStatus(null), 2000);
      } else {
        setFeedbackStatus("error");
      }
    } catch {
      setFeedbackStatus("error");
    }
  }

  function handleCopy() {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  if (role === "user") {
    return (
      <div className="flex justify-end items-start gap-2 my-3 group">
        <div className="flex flex-col items-end gap-1">
          {editing ? (
            <div className="flex flex-col gap-2 w-[60vw] max-w-xl">
              <textarea
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                autoFocus
                rows={3}
                className="w-full rounded-xl border px-3 py-2 text-sm resize-none"
                style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)", color: "var(--text)" }}
              />
              <div className="flex gap-2 justify-end">
                <button
                  onClick={() => { setEditing(false); setEditValue(content); }}
                  className="text-xs px-2 py-1 rounded-lg border"
                  style={{ borderColor: "var(--surface-border)" }}
                >
                  Cancel
                </button>
                <button
                  onClick={() => { setEditing(false); onEdit?.(editValue); }}
                  className="text-xs px-2 py-1 rounded-lg text-white"
                  style={{ background: "var(--accent)" }}
                >
                  Save & submit
                </button>
              </div>
            </div>
          ) : (
            <>
              <div
                className="rounded-2xl px-4 py-2 text-sm max-w-[60vw]"
                style={{ background: "var(--user-bubble-bg)", color: "var(--user-bubble-text)" }}
              >
                {content}
              </div>
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button onClick={handleCopy} className="p-1 rounded hover:bg-[var(--accent-soft)]" title="Copy">
                  {copied ? <Check size={12} style={{ color: "var(--accent)" }} /> : <Copy size={12} style={{ color: "var(--muted)" }} />}
                </button>
                {isLastUser && (
                  <>
                    <button onClick={() => setEditing(true)} className="p-1 rounded hover:bg-[var(--accent-soft)]" title="Edit">
                      <Pencil size={12} style={{ color: "var(--muted)" }} />
                    </button>
                    <button onClick={onRegenerate} className="p-1 rounded hover:bg-[var(--accent-soft)]" title="Regenerate">
                      <RotateCcw size={12} style={{ color: "var(--muted)" }} />
                    </button>
                  </>
                )}
              </div>
            </>
          )}
        </div>
        <span className="text-xs whitespace-nowrap pt-2" style={{ color: "var(--muted)" }}>{ts}</span>
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
        {messageId && !streaming && (
          <div className="flex items-center gap-2 mt-2">
            <button
              onClick={() => sendFeedback("up")}
              disabled={feedbackStatus === "saving"}
              className="p-1.5 rounded-lg transition-colors"
              style={{ background: feedback === "up" ? "var(--accent-soft)" : "transparent" }}
            >
              <ThumbsUp size={13} style={{ color: feedback === "up" ? "var(--accent)" : "var(--muted)" }} />
            </button>
            <button
              onClick={() => sendFeedback("down")}
              disabled={feedbackStatus === "saving"}
              className="p-1.5 rounded-lg transition-colors"
              style={{ background: feedback === "down" ? "var(--accent-soft)" : "transparent" }}
            >
              <ThumbsDown size={13} style={{ color: feedback === "down" ? "var(--accent)" : "var(--muted)" }} />
            </button>
            {feedbackStatus === "saved" && <span className="text-xs" style={{ color: "var(--muted)" }}>Thanks for the feedback</span>}
            {feedbackStatus === "error" && <span className="text-xs text-red-500">Couldn't save — try again</span>}
          </div>
        )}
      </div>
    </div>
  );
}