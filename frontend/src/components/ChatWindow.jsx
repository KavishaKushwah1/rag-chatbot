import { useEffect, useRef, useState } from "react";
import { Paperclip, ArrowRight, MoreHorizontal, Sun, Moon, X, FileIcon } from "lucide-react";
import { extractAttachment, fetchSessionMessages, renameSession, streamChat } from "../api";
import Message from "./Message";
import EmptyState from "./EmptyState";
import WarningCard from "./WarningCard";
import DeleteConfirmModal from "./DeleteConfirmModal";
import SourceModal from "./SourceModal";
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
  const [viewingSource, setViewingSource] = useState(null);
  const [attachedFiles, setAttachedFiles] = useState([]);
  const bottomRef = useRef(null);
  const headerMenuRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!sessionId) { setMessages([]); setTitle("Acme Knowledge Assistant"); return; }
    fetchSessionMessages(token, sessionId).then((raw) => {
      setMessages(raw.map((m) => ({ role: m.role, content: m.content, ts: fmtTime(m.created_at), sources: [] })));
    });
  }, [sessionId]);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, streamingText]);

  useEffect(() => {
    function handleClickOutside(e) {
      if (headerMenuRef.current && !headerMenuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen]);

  async function handleSend() {
    const query = input.trim();
    if (!query) return;
    setInput("");
    setError(null);

    const userTs = fmtTime();
    setMessages((prev) => [...prev, { role: "user", content: query, ts: userTs }]);

    let attachedContext = [];
    if (attachedFiles.length > 0) {
      try {
        attachedContext = await Promise.all(
          attachedFiles.map(async (file) => {
            const result = await extractAttachment(token, file);
            return { filename: result.filename, text: result.text };
          })
        );
      } catch (err) {
        setError(err.message);
        return;
      }
    }
    setAttachedFiles([]);

    let finalText = "";
    let finalSources = [];
    let finalAttachments = [];
    setStreamingText("");
    setStreamingSources([]);

    await streamChat(token, query, sessionId, attachedContext, {
      onSession: (id) => { setSessionId(id); onSessionsChanged(); },
      onSources: (s) => { finalSources = s; setStreamingSources(s); },
      onAttachments: (names) => { finalAttachments = names; },
      onToken: (t) => { finalText += t; setStreamingText(finalText); },
      onError: (msg) => setError(msg),
      onAuthError: () => onSignOutExpired(),
      onDone: () => {
        setMessages((prev) => [...prev, {
          role: "assistant", content: finalText, ts: fmtTime(),
          sources: finalSources, usedAttachments: finalAttachments,
        }]);
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

  function handleAttachClick() {
    fileInputRef.current?.click();
  }

  function handleFilesSelected(e) {
    const files = Array.from(e.target.files || []);
    setAttachedFiles((prev) => [...prev, ...files]);
    e.target.value = "";
  }

  function removeAttachedFile(index) {
    setAttachedFiles((prev) => prev.filter((_, i) => i !== index));
  }

  return (
    <div className="flex-1 flex flex-col h-screen">
      <div className="flex items-center justify-between px-7 py-5">
        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-xl border shadow-sm transition-colors hover:border-[var(--accent)]"
            style={{ borderColor: "var(--surface-border)" }}
          >
            {theme === "light" ? <Moon size={16} /> : <Sun size={16} />}
          </button>
          {sessionId && (
            <div className="relative" ref={headerMenuRef}>
              <button
                onClick={() => setMenuOpen((o) => !o)}
                className="p-2.5 rounded-xl border shadow-sm transition-colors hover:border-[var(--accent)]"
                style={{ borderColor: "var(--surface-border)" }}
              >
                <MoreHorizontal size={16} />
              </button>
              {menuOpen && (
                <div className="absolute right-0 top-12 z-10 w-48 rounded-xl border shadow-md p-1.5 text-sm"
                  style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)" }}>
                  <button
                    onClick={() => { const t = prompt("New title", title); if (t) handleRename(t); setMenuOpen(false); }}
                    className="w-full text-left px-2.5 py-2 rounded-lg transition-colors hover:bg-[var(--accent-soft)]"
                  >
                    Rename this chat
                  </button>
                  <button
                    onClick={() => { setMenuOpen(false); setConfirmDelete(true); }}
                    className="w-full text-left px-2.5 py-2 rounded-lg text-red-500 transition-colors hover:bg-red-50"
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
          <Message key={i} role={m.role} content={m.content} ts={m.ts} sources={m.sources} usedAttachments={m.usedAttachments} onSourceClick={setViewingSource} />
        ))}

        {streamingText !== null && (
          <Message role="assistant" content={streamingText} ts="" sources={streamingSources} streaming onSourceClick={setViewingSource} />
        )}

        {error && <WarningCard>{error}</WarningCard>}
        <div ref={bottomRef} />
      </div>

      <div className="px-7 pb-4 pt-2">
        {attachedFiles.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-2">
            {attachedFiles.map((f, i) => (
              <div
                key={i}
                className="flex items-center gap-1.5 rounded-lg border px-2.5 py-1.5 text-xs"
                style={{ background: "var(--surface)", borderColor: "var(--surface-border)" }}
              >
                <FileIcon size={13} style={{ color: "var(--accent)" }} />
                <span className="max-w-[160px] truncate">{f.name}</span>
                <button onClick={() => removeAttachedFile(i)} className="ml-1">
                  <X size={12} style={{ color: "var(--muted)" }} />
                </button>
              </div>
            ))}
          </div>
        )}

        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.md"
          onChange={handleFilesSelected}
          className="hidden"
        />

        <div
          className="flex items-center gap-2.5 rounded-2xl border px-4 py-3 shadow-sm transition-shadow focus-within:shadow-md focus-within:ring-2"
          style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)" }}
        >
          <button onClick={handleAttachClick} className="flex-shrink-0" title="Attach a file (.pdf, .doc, .docx, .zip)">
            <Paperclip size={16} style={{ color: "var(--muted)" }} />
          </button>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask about HR policy, engineering docs, or pricing…"
            className="flex-1 bg-transparent outline-none text-sm"
          />
          <button
            onClick={handleSend}
            className="p-2 rounded-full text-white transition-transform hover:scale-105"
            style={{ background: "var(--accent)" }}
          >
            <ArrowRight size={16} />
          </button>
        </div>
        <div className="text-center text-xs mt-2.5" style={{ color: "var(--muted)" }}>
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

      {viewingSource && (
        <SourceModal source={viewingSource} onClose={() => setViewingSource(null)} />
      )}
    </div>
  );
}