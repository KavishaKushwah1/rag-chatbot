import { useEffect, useState } from "react";
import { Plus, Folder, ChevronRight } from "lucide-react";
import { fetchSessions } from "../api";
import SessionRow from "./SessionRow";

export default function Sidebar({
  token, currentSessionId, onNewChat, onOpenSession, onDeleteRequest,
  me, refreshKey, onOpenAccountMenu,
}) {
  const [sessions, setSessions] = useState([]);

  async function reload() {
    setSessions(await fetchSessions(token));
  }
  useEffect(() => { reload(); }, [refreshKey]);

  const pinned = sessions.filter((s) => s.pinned);
  const recent = sessions.filter((s) => !s.pinned);
  const letter = (me?.display_name || me?.email || "?").trim()[0]?.toUpperCase();

  return (
    <div
      className="w-80 flex flex-col border-r h-screen sticky top-0 px-3 py-4"
      style={{ background: "var(--surface)", borderColor: "var(--surface-border)" }}
    >
      <div className="flex items-center gap-2 px-1 pb-4">
        <Folder size={22} />
        <div>
          <div className="font-semibold text-sm">Acme</div>
          <div className="text-xs" style={{ color: "var(--muted)" }}>Knowledge Assistant</div>
        </div>
      </div>

      <button
        onClick={onNewChat}
        className="flex items-center justify-center gap-1 rounded-lg border py-2 text-sm mb-4"
        style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)" }}
      >
        <Plus size={14} /> New chat
      </button>

      <div className="flex-1 overflow-y-auto">
        {pinned.length > 0 && (
          <>
            <div className="text-xs font-medium px-1 mb-1" style={{ color: "var(--muted)" }}>Pinned</div>
            {pinned.map((s) => (
              <SessionRow key={s.session_id} session={s} isCurrent={s.session_id === currentSessionId}
                token={token} onOpen={onOpenSession} onChanged={reload} onDeleteRequest={onDeleteRequest} />
            ))}
            <div className="border-t my-3" style={{ borderColor: "var(--surface-border)" }} />
          </>
        )}

        <div className="text-xs font-medium px-1 mb-1" style={{ color: "var(--muted)" }}>Recent conversations</div>
        {recent.length === 0 && <div className="text-xs px-1" style={{ color: "var(--muted)" }}>No conversations yet.</div>}
        {recent.map((s) => (
          <SessionRow key={s.session_id} session={s} isCurrent={s.session_id === currentSessionId}
            token={token} onOpen={onOpenSession} onChanged={reload} onDeleteRequest={onDeleteRequest} />
        ))}
      </div>

      <button
        onClick={onOpenAccountMenu}
        className="flex items-center gap-2 pt-3 mt-2 border-t"
        style={{ borderColor: "var(--surface-border)" }}
      >
        <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold text-white" style={{ background: "var(--avatar-bg)" }}>
          {letter}
        </div>
        <div className="text-left">
          <div className="text-sm font-medium">{me?.display_name || me?.email}</div>
          <div className="text-xs" style={{ color: "var(--muted)" }}>Free plan</div>
        </div>
        <ChevronRight size={14} className="ml-auto" style={{ color: "var(--muted)" }} />
      </button>
    </div>
  );
}