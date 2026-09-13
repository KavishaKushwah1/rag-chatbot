import { useEffect, useState } from "react";
import { X, ThumbsUp, ThumbsDown, Upload, Trash2 } from "lucide-react";
import { formatContent } from "./Message";

const BASE = import.meta.env.VITE_BACKEND_URL;

export default function AdminPanel({ token, onClose }) {
  const [tab, setTab] = useState("users");
  const [users, setUsers] = useState([]);
  const [audit, setAudit] = useState([]);
  const [feedback, setFeedback] = useState(null);
  const [docs, setDocs] = useState([]);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadPerms, setUploadPerms] = useState(["public"]);

  function togglePerm(perm) {
    setUploadPerms((prev) =>
      prev.includes(perm) ? prev.filter((p) => p !== perm) : [...prev, perm]
    );
  }

  async function authedGet(path) {
    const res = await fetch(`${BASE}${path}`, { headers: { Authorization: `Bearer ${token}` } });
    return res.ok ? res.json() : null;
  }

  async function loadAll() {
    setUsers((await authedGet("/admin/users")) || []);
    setAudit((await authedGet("/admin/audit-log")) || []);
    setFeedback(await authedGet("/admin/feedback-summary"));
    setDocs((await authedGet("/admin/documents")) || []);
  }
  useEffect(() => { loadAll(); }, []);

  async function changeDepartment(userId, department) {
    await fetch(`${BASE}/admin/users/${userId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ department }),
    });
    loadAll();
  }

  async function handleUpload() {
    if (!uploadFile || uploadPerms.length === 0) return;
    const formData = new FormData();
    formData.append("file", uploadFile);
    formData.append("permissions", uploadPerms.join(","));
    await fetch(`${BASE}/admin/documents`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });
    setUploadFile(null);
    loadAll();
  }

  async function deleteDoc(docId) {
    if (!confirm(`Delete "${docId}" from the knowledge base?`)) return;
    await fetch(`${BASE}/admin/documents/${docId}`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
    loadAll();
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="w-full max-w-3xl max-h-[85vh] overflow-y-auto rounded-xl border p-6"
        style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-lg font-semibold">Admin Panel</h2>
          <button onClick={onClose}><X size={18} /></button>
        </div>

        <div className="flex gap-4 mb-5 text-sm border-b" style={{ borderColor: "var(--surface-border)" }}>
          {["users", "audit", "feedback", "documents"].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className="pb-2 capitalize"
              style={{
                color: tab === t ? "var(--accent)" : "var(--muted)",
                borderBottom: tab === t ? "2px solid var(--accent)" : "none",
              }}
            >
              {t}
            </button>
          ))}
        </div>

        {tab === "users" && (
          <div className="space-y-2">
            {users.map((u) => (
              <div key={u.id} className="flex items-center justify-between text-sm border rounded-lg px-3 py-2" style={{ borderColor: "var(--surface-border)" }}>
                <div>{u.display_name || u.email}</div>
                <select
                  value={u.department}
                  onChange={(e) => changeDepartment(u.id, e.target.value)}
                  className="border rounded px-2 py-1 text-xs"
                  style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)", color: "var(--text)" }}
                >
                  {["public", "hr", "engineering", "manager", "admin"].map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
            ))}
          </div>
        )}

        {tab === "audit" && (
          <div className="space-y-2 text-xs">
            {audit.map((a, i) => (
              <div key={i} className="border rounded-lg px-3 py-2" style={{ borderColor: "var(--surface-border)" }}>
                {a.old_department || "none"} → <b>{a.new_department}</b>
                <div style={{ color: "var(--muted)" }}>{new Date(a.changed_at).toLocaleString()}</div>
              </div>
            ))}
            {audit.length === 0 && <div style={{ color: "var(--muted)" }}>No role changes yet.</div>}
          </div>
        )}

        {tab === "feedback" && feedback && (
          <div>
            <div className="flex gap-6 mb-4 text-sm">
              <div className="flex items-center gap-1"><ThumbsUp size={14} /> {feedback.thumbs_up}</div>
              <div className="flex items-center gap-1"><ThumbsDown size={14} /> {feedback.thumbs_down}</div>
            </div>
            {feedback.negative_feedback_summary ? (
              <div className="mb-5 border rounded-lg p-3 text-sm" style={{ borderColor: "var(--surface-border)", background: "var(--surface)" }}>
                <div className="text-xs font-medium mb-1" style={{ color: "var(--muted)" }}>
                  Insight from {feedback.negative_feedback_count} negative ratings
                </div>
                <div dangerouslySetInnerHTML={{ __html: formatContent(feedback.negative_feedback_summary) }} />
              </div>
            ) : (
              <div className="mb-5 text-xs" style={{ color: "var(--muted)" }}>
                Need at least 5 negative ratings to generate insights (currently {feedback.negative_feedback_count}).
              </div>
            )}
            <div className="text-xs font-medium mb-2" style={{ color: "var(--muted)" }}>Recent unanswered questions</div>
            <div className="space-y-1 text-sm">
              {feedback.unanswered_questions.map((q, i) => (
                <div key={i} className="border rounded-lg px-3 py-2" style={{ borderColor: "var(--surface-border)" }}>
                  <div>{q.question}</div>
                  <div className="text-xs mt-1" style={{ color: "var(--muted)" }}>
                    {new Date(q.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
              {feedback.unanswered_questions.length === 0 && <div style={{ color: "var(--muted)" }}>None yet.</div>}
            </div>
          </div>
        )}

        {tab === "documents" && (
          <div>
            <div className="flex flex-wrap items-center gap-3 mb-4">
              <input type="file" accept=".pdf,.docx,.txt,.md" onChange={(e) => setUploadFile(e.target.files[0])} className="text-xs" />

              <div className="flex gap-2">
                {["public", "hr", "engineering", "manager"].map((p) => (
                  <label key={p} className="flex items-center gap-1 text-xs border rounded-lg px-2 py-1 cursor-pointer" style={{ borderColor: uploadPerms.includes(p) ? "var(--accent)" : "var(--surface-border)", background: uploadPerms.includes(p) ? "var(--accent-soft)" : "transparent" }}>
                    <input type="checkbox" checked={uploadPerms.includes(p)} onChange={() => togglePerm(p)} className="hidden" />
                    {p}
                  </label>
                ))}
              </div>

              <button onClick={handleUpload} className="flex items-center gap-1 rounded-lg px-3 py-1 text-xs text-white" style={{ background: "var(--accent)" }}>
                <Upload size={13} /> Upload
              </button>
            </div>
            <div className="space-y-2">
              {docs.map((d) => (
                <div key={d.doc_id} className="flex items-center justify-between text-sm border rounded-lg px-3 py-2" style={{ borderColor: "var(--surface-border)" }}>
                  <div>
                    <div>{d.source}</div>
                    <div className="text-xs" style={{ color: "var(--muted)" }}>
                      {Array.isArray(d.permission) ? d.permission.join(", ") : d.permission} · {d.chunk_count} chunks
                    </div>
                  </div>
                  <button onClick={() => deleteDoc(d.doc_id)} className="p-1 rounded hover:bg-red-50">
                    <Trash2 size={14} className="text-red-500" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}