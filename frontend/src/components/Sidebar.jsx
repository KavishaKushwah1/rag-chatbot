import { useEffect, useRef, useState } from "react";
import { Plus, Settings, LogOut, Shield } from "lucide-react";
import { fetchSessions } from "../api";
import SessionRow from "./SessionRow";
import { useTheme } from "../context/ThemeContext";
import logoDark from "../assets/logo-dark.png";
import logoLight from "../assets/logo-light.png";

export default function Sidebar({
  token, currentSessionId, onNewChat, onOpenSession, onDeleteRequest,
  me, refreshKey, onSignOut, onOpenSettings, onOpenAdmin,
}) {
  const { theme } = useTheme();
  const [sessions, setSessions] = useState([]);
  const [menuOpen, setMenuOpen] = useState(false);
  const [openMenuId, setOpenMenuId] = useState(null);
  const menuRef = useRef(null);

  async function reload() {
    setSessions(await fetchSessions(token));
  }
  useEffect(() => { reload(); }, [refreshKey]);

  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
      if (openMenuId !== null && !e.target.closest("[data-session-menu-root]")) {
        setOpenMenuId(null);
      }
    }
    if (menuOpen || openMenuId !== null) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen, openMenuId]);

  const pinned = sessions.filter((s) => s.pinned);
  const recent = sessions.filter((s) => !s.pinned);
  const letter = (me?.display_name || me?.email || "?").trim()[0]?.toUpperCase();
  const logoSrc = theme === "dark" ? logoDark : logoLight;

  return (
    <div
      className="w-80 flex flex-col border-r h-screen sticky top-0 px-3 py-5"
      style={{ background: "var(--surface)", borderColor: "var(--surface-border)" }}
    >
      <div className="flex items-center gap-2.5 px-1 pb-5">
        <img
          src={logoSrc}
          alt="Acme logo"
          className="w-9 h-9 rounded-xl object-contain flex-shrink-0"
        />
        <div>
          <div className="font-semibold text-sm leading-tight">Acme</div>
          <div className="text-xs" style={{ color: "var(--muted)" }}>Knowledge Assistant</div>
        </div>
      </div>

      <button
        onClick={onNewChat}
        className="flex items-center justify-center gap-1.5 rounded-xl border py-2.5 text-sm font-medium mb-5 shadow-sm transition-colors hover:border-[var(--accent)]"
        style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)" }}
      >
        <Plus size={15} /> New chat
      </button>

      <div className="flex-1 overflow-y-auto -mx-1 px-1 space-y-0.5">
        {pinned.length > 0 && (
          <>
            <div className="text-xs font-medium px-2 mb-1.5 mt-1" style={{ color: "var(--muted)" }}>Pinned</div>
            {pinned.map((s) => (
              <SessionRow key={s.session_id} session={s} isCurrent={s.session_id === currentSessionId}
                token={token} onOpen={onOpenSession} onChanged={reload} onDeleteRequest={onDeleteRequest}
                isMenuOpen={openMenuId === s.session_id}
                onToggleMenu={(id) => setOpenMenuId((prev) => (id === null ? null : prev === id ? null : id))} />
            ))}
            <div className="border-t my-3" style={{ borderColor: "var(--surface-border)" }} />
          </>
        )}

        <div className="text-xs font-medium px-2 mb-1.5 mt-1" style={{ color: "var(--muted)" }}>Recent conversations</div>
        {recent.length === 0 && (
          <div className="text-xs px-2 py-1" style={{ color: "var(--muted)" }}>No conversations yet.</div>
        )}
        {recent.map((s) => (
          <SessionRow key={s.session_id} session={s} isCurrent={s.session_id === currentSessionId}
            token={token} onOpen={onOpenSession} onChanged={reload} onDeleteRequest={onDeleteRequest}
            isMenuOpen={openMenuId === s.session_id}
            onToggleMenu={(id) => setOpenMenuId((prev) => (id === null ? null : prev === id ? null : id))} />
        ))}
      </div>

      <div className="relative pt-3 mt-2 border-t" style={{ borderColor: "var(--surface-border)" }} ref={menuRef}>
        <button
          onClick={() => setMenuOpen((o) => !o)}
          className="w-full flex items-center gap-2.5 rounded-xl px-2 py-2 transition-colors hover:bg-[var(--accent-soft)]"
        >
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold text-white flex-shrink-0"
            style={{ background: "var(--avatar-bg)" }}
          >
            {letter}
          </div>
          <div className="text-left min-w-0">
            <div className="text-sm font-medium truncate">{me?.display_name || me?.email}</div>
            {me?.department && (
              <span
                className="inline-block text-[10px] font-medium px-1.5 py-0.5 rounded-md mt-0.5 capitalize"
                style={{ background: "var(--accent-soft)", color: "var(--accent)" }}
              >
                {me.department}
              </span>
            )}
          </div>
        </button>

        {menuOpen && (
          <div
            className="absolute left-0 bottom-full mb-2 w-full rounded-xl border shadow-md p-1.5 text-sm z-20"
            style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)" }}
          >
            {me?.department === "admin" && (
              <button
                onClick={() => { setMenuOpen(false); onOpenAdmin(); }}
                className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg transition-colors hover:bg-[var(--accent-soft)]"
              >
                <Shield size={15} style={{ color: "var(--muted)" }} /> Admin Panel
              </button>
            )}
            <button
              onClick={() => { setMenuOpen(false); onOpenSettings(); }}
              className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg transition-colors hover:bg-[var(--accent-soft)]"
            >
              <Settings size={15} style={{ color: "var(--muted)" }} /> Settings
            </button>
            <button
              onClick={() => { setMenuOpen(false); onSignOut(); }}
              className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg transition-colors hover:bg-[var(--accent-soft)]"
            >
              <LogOut size={15} style={{ color: "var(--muted)" }} /> Log out
            </button>
          </div>
        )}
      </div>
    </div>
  );
}