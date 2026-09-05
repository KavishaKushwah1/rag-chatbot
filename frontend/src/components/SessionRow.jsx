import { useState } from "react";
import { Pin, PinOff, Pencil } from "lucide-react";
import { pinSession, renameSession } from "../api";

export default function SessionRow({
  session, isCurrent, token, onOpen, onChanged, onDeleteRequest,
  isMenuOpen, onToggleMenu,
}) {
  const [renaming, setRenaming] = useState(false);
  const [title, setTitle] = useState(session.preview);

  async function handlePin() {
    await pinSession(token, session.session_id, !session.pinned);
    onToggleMenu(null);
    onChanged();
  }

  async function handleRenameSave() {
    await renameSession(token, session.session_id, title);
    setRenaming(false);
    onToggleMenu(null);
    onChanged();
  }

  return (
    <div className="relative flex items-center gap-1" data-session-menu-root>
      <button
        onClick={() => onOpen(session.session_id)}
        className="flex-1 flex items-center gap-2 text-left text-sm rounded-xl px-2.5 py-2 truncate transition-colors hover:bg-[var(--accent-soft)]"
      >
        {isCurrent && <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)] flex-shrink-0" />}
        <span className="truncate">{session.preview}</span>
      </button>

      <button
        onClick={() => { setRenaming(false); onToggleMenu(session.session_id); }}
        className="p-1 rounded hover:bg-[var(--accent-soft)]"
      >
        ⋮
      </button>

      {isMenuOpen && (
        <div
          className="absolute right-0 top-8 z-20 w-44 rounded-xl border shadow-md p-1.5 text-sm"
          style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)" }}
        >
          {!renaming ? (
            <>
              <button onClick={handlePin} className="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-[var(--accent-soft)]">
                {session.pinned ? <PinOff size={14} /> : <Pin size={14} />} {session.pinned ? "Unpin" : "Pin"}
              </button>
              <button onClick={() => setRenaming(true)} className="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-[var(--accent-soft)]">
                <Pencil size={14} /> Rename
              </button>
              <div className="border-t my-1" style={{ borderColor: "var(--surface-border)" }} />
              <button
                onClick={() => { onToggleMenu(null); onDeleteRequest(session.session_id, isCurrent); }}
                className="w-full text-left px-2 py-1.5 rounded-lg text-red-500 hover:bg-red-50"
              >
                Delete
              </button>
            </>
          ) : (
            <div className="p-1">
              <input
                value={title} onChange={(e) => setTitle(e.target.value)} autoFocus
                className="w-full rounded-lg border px-2 py-1 text-sm mb-1"
                style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)", color: "var(--text)" }}
              />
              <button onClick={handleRenameSave} className="w-full rounded-lg py-1 text-sm text-white" style={{ background: "var(--accent)" }}>
                Save
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}