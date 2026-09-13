const BASE = import.meta.env.VITE_BACKEND_URL;

async function authedFetch(path, token, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: { ...options.headers, Authorization: `Bearer ${token}` },
  });
  return res;
}

export async function fetchMe(token) {
  const res = await authedFetch("/me", token);
  return res.ok ? res.json() : null;
}

export async function updateDisplayName(token, display_name) {
  const res = await authedFetch("/me", token, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ display_name }),
  });
  return res.ok;
}

export async function fetchSessions(token) {
  const res = await authedFetch("/sessions", token);
  return res.ok ? res.json() : [];
}

export async function fetchSessionMessages(token, sessionId) {
  const res = await authedFetch(`/sessions/${sessionId}/messages`, token);
  return res.ok ? res.json() : [];
}

export async function renameSession(token, sessionId, title) {
  const res = await authedFetch(`/sessions/${sessionId}`, token, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  return res.ok;
}

export async function pinSession(token, sessionId, pinned) {
  const res = await authedFetch(`/sessions/${sessionId}`, token, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pinned }),
  });
  return res.ok;
}

export async function deleteSession(token, sessionId) {
  const res = await authedFetch(`/sessions/${sessionId}`, token, { method: "DELETE" });
  return res.ok;
}

export async function submitFeedback(token, messageId, rating) {
  const res = await authedFetch(`/messages/${messageId}/feedback`, token, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ rating }),
  });
  return res.ok;
}

export async function extractAttachment(token, file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BASE}/attachments/extract`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to read ${file.name}`);
  }
  return res.json();
}

/**
 * Streams /chat via fetch + ReadableStream (EventSource can't send auth headers,
 * so we parse the SSE frames manually — same approach as the Python CLI clients).
 */
export async function streamChat(token, query, sessionId, attachedContext, callbacks) {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ query, session_id: sessionId, attached_context: attachedContext }),
  });

  if (res.status === 401) return callbacks.onAuthError?.();
  if (!res.ok) return callbacks.onError?.(`HTTP ${res.status}`);

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let currentEvent = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop();

    for (const line of lines) {
      if (line.startsWith("event:")) {
        currentEvent = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        const data = line.slice(5).trim();
        if (currentEvent === "session") callbacks.onSession?.(JSON.parse(data).session_id);
        else if (currentEvent === "message_id") callbacks.onMessageId?.(JSON.parse(data).message_id);
        else if (currentEvent === "sources") callbacks.onSources?.(JSON.parse(data));
        else if (currentEvent === "attachments") callbacks.onAttachments?.(JSON.parse(data));
        else if (currentEvent === "token") callbacks.onToken?.(data);
        else if (currentEvent === "error") callbacks.onError?.(JSON.parse(data).message);
        else if (currentEvent === "done") callbacks.onDone?.();
      }
    }
  }
}