import { X, Sun, Moon } from "lucide-react";
import { useState } from "react";
import { useTheme } from "../context/ThemeContext";
import { updateDisplayName } from "../api";

export default function SettingsModal({ me, token, onClose, onSaved }) {
  const { theme, setTheme } = useTheme();
  const [name, setName] = useState(me?.display_name || "");
  const letter = (me?.display_name || me?.email || "?").trim()[0]?.toUpperCase();

  async function handleSave() {
    if (await updateDisplayName(token, name)) {
      onSaved(name);
      onClose();
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="w-full max-w-sm rounded-xl border p-6"
        style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-lg font-semibold">Settings</h2>
          <button onClick={onClose}><X size={18} /></button>
        </div>

        <div className="flex items-center gap-3 mb-5">
          <div
            className="w-14 h-14 rounded-full flex items-center justify-center text-xl font-semibold text-white"
            style={{ background: "var(--avatar-bg)" }}
          >
            {letter}
          </div>
          <div className="text-xs" style={{ color: "var(--muted)" }}>
            Generated from your display name.<br />Updates automatically when you change it below.
          </div>
        </div>

        <label className="text-sm font-medium">Display name</label>
        <input
          value={name} onChange={(e) => setName(e.target.value)}
          className="w-full mt-1 mb-5 rounded-lg border px-3 py-2 text-sm"
          style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)", color: "var(--text)" }}
        />

        <label className="text-sm font-medium">Appearance</label>
        <div className="flex gap-2 mt-2 mb-5">
          <button
            onClick={() => setTheme("light")}
            className="flex-1 flex items-center justify-center gap-2 rounded-lg border py-2 text-sm"
            style={{
              borderColor: theme === "light" ? "var(--accent)" : "var(--surface-border)",
              background: theme === "light" ? "var(--accent-soft)" : "transparent",
            }}
          >
            <Sun size={14} /> Light
          </button>
          <button
            onClick={() => setTheme("dark")}
            className="flex-1 flex items-center justify-center gap-2 rounded-lg border py-2 text-sm"
            style={{
              borderColor: theme === "dark" ? "var(--accent)" : "var(--surface-border)",
              background: theme === "dark" ? "var(--accent-soft)" : "transparent",
            }}
          >
            <Moon size={14} /> Dark
          </button>
        </div>

        <div className="text-xs mb-1" style={{ color: "var(--muted)" }}>Signed in as <b>{me?.email}</b></div>
        <div className="text-xs mb-5 capitalize" style={{ color: "var(--muted)" }}>{me?.department || "public"}</div>

        <div className="flex gap-2">
          <button onClick={onClose} className="flex-1 rounded-lg border py-2 text-sm" style={{ borderColor: "var(--surface-border)" }}>
            Cancel
          </button>
          <button onClick={handleSave} className="flex-1 rounded-lg py-2 text-sm text-white" style={{ background: "var(--accent)" }}>
            Save
          </button>
        </div>
      </div>
    </div>
  );
}