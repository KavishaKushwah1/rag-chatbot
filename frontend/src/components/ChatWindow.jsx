import { useEffect, useRef, useState } from "react";
import { Paperclip, ArrowRight, MoreHorizontal, Sun, Moon } from "lucide-react";
import { fetchSessionMessages, renameSession, streamChat } from "../api";
import Message from "./Message";
import EmptyState from "./EmptyState";
import WarningCard from "./WarningCard";
import DeleteConfirmModal from "./DeleteConfirmModal";
import { useTheme } from "../context/ThemeContext";

function fmtTime(iso) {
  const d = iso ? new Date(iso) : new Date();
  return d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
}

export default function ChatWindow({ token, me, sessionId, setSessionId, onSessionsChanged, onSignOutExpired }) {
  const { theme, toggleTheme } = useTheme();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [streamingText, setStreamingText] = useState(null);
  const [streamingSources, setStreamingSources] = useState([]);
  const [error, setError] = useState(null);
  const [title, setTitle] = useState("Acme Knowledge Assistant");
  const [menuOpen, setMenuOpen] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    if (!sessionId) { setMessages([]); setTitle("Acme Knowledge Assistant"); return; }
    fetchSessionMessages(token, sessionId).then((raw) => {
      setMessages(raw.map((m) => ({ role: m.role, content: m.content, ts: fmtTime(m.created_at), sources: [] })));
    });
  }, [sessionId]);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, streamingText]);

  async function handleSend() {
    const query = input.trim();
    if (!query) return;
    setInput("");
    setError(null);
    const userTs = fmtTime();
    setMessages((prev) => [...prev, { role: "user", content: query, ts: userTs }]);

    let finalText = "";
    let finalSources = [];
    setStreamingText("");
    setStreamingSources([]);

    await streamChat(token, query, sessionId, {
      onSession: (id) => { setSessionId(id); onSessionsChanged(); },
      onSources: (s) => { finalSources = s; setStreamingSources(s); },
      onToken: (t) => { finalText += t; setStreamingText(finalText); },
      onError: (msg) => setError(msg),
      onAuthError: () => onSignOutExpired(),
      onDone: () => {
        setMessages((prev) => [...prev, { role: "assistant", content: finalText, ts: fmtTime(), sources: finalSources }]);
        setStreamingText(null);
        setStreamingSources([]);
        onSessionsChanged();
      },
    });
  }

  async function handleRename(newTitle) {
    if (!sessionId) return;
    await renameSession(token, sessionId, newTitle);
    setTitle(newTitle);
    onSessionsChanged();
  }

  return (
    <div className="flex-1 flex flex-col h-screen">
      <div className="flex items-center justify-between px-6 py-4">
        <h1 className="text-xl font-semibold">{title}</h1>
        <div className="flex items-center gap-2">
          <button onClick={toggleTheme} className="p-2 rounded-lg border" style={{ borderColor: "var(--surface-border)" }}>
            {theme === "light" ? <Moon size={16} /> : <Sun size={16} />}
          </button>
          {sessionId && (
            <div className="relative">
              <button onClick={() => setMenuOpen((o) => !o)} className="p-2 rounded-lg border" style={{ borderColor: "var(--surface-border)" }}>
                <MoreHorizontal size={16} />
              </button>
              {menuOpen && (
                <div className="absolute right-0 top-10 z-10 w-48 rounded-lg border p-1 text-sm"
                  style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)" }}>
                  <button
                    onClick={() => { const t = prompt("New title", title); if (t) handleRename(t); setMenuOpen(false); }}
                    className="w-full text-left px-2 py-1.5 rounded hover:bg-[var(--accent-soft)]"
                  >
                    Rename this chat
                  </button>
                  <button
                    onClick={() => { setMenuOpen(false); setConfirmDelete(true); }}
                    className="w-full text-left px-2 py-1.5 rounded text-red-500 hover:bg-red-50"
                  >
                    Delete this chat
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-6">
        {messages.length === 0 && streamingText === null && <EmptyState displayName={me?.display_name} />}

        {messages.map((m, i) => (
          <Message key={i} role={m.role} content={m.content} ts={m.ts} sources={m.sources} />
        ))}

        {streamingText !== null && (
          <Message role="assistant" content={streamingText} ts="" sources={streamingSources} streaming />
        )}

        {error && <WarningCard>{error}</WarningCard>}
        <div ref={bottomRef} />
      </div>

      <div className="px-6 pb-3 pt-2">
        <div
          className="flex items-center gap-2 rounded-xl border px-3 py-2 focus-within:ring-2"
          style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)" }}
        >
          <Paperclip size={16} style={{ color: "var(--muted)" }} />
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask about HR policy, engineering docs, or pricing…"
            className="flex-1 bg-transparent outline-none text-sm"
          />
          <button onClick={handleSend} className="p-1.5 rounded-full text-white" style={{ background: "var(--accent)" }}>
            <ArrowRight size={16} />
          </button>
        </div>
        <div className="text-center text-xs mt-2" style={{ color: "var(--muted)" }}>
          Acme Knowledge Assistant can make mistakes. Always verify important information.
        </div>
      </div>

      {confirmDelete && (
        <DeleteConfirmModal
          onCancel={() => setConfirmDelete(false)}
          onConfirm={async () => {
            const { deleteSession } = await import("../api");
            await deleteSession(token, sessionId);
            setSessionId(null);
            setConfirmDelete(false);
            onSessionsChanged();
          }}
        />
      )}
    </div>
  );
}