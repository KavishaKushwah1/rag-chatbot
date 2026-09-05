import { FileText } from "lucide-react";
import SourceCards from "./SourceCards";

export default function Message({ role, content, ts, sources, streaming }) {
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
        <div className="text-sm leading-relaxed whitespace-pre-wrap">
          {content}{streaming && <span className="animate-pulse">▌</span>}
        </div>
        <SourceCards sources={sources} />
      </div>
      <span className="text-xs whitespace-nowrap pt-2" style={{ color: "var(--muted)" }}>{ts}</span>
    </div>
  );
}