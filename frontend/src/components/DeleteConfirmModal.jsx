export default function DeleteConfirmModal({ onCancel, onConfirm }) {
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={onCancel}>
      <div
        className="w-full max-w-xs rounded-xl border p-5"
        style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)" }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className="font-semibold mb-2">Delete conversation?</h3>
        <p className="text-sm mb-4" style={{ color: "var(--muted)" }}>
          This will permanently delete this conversation. This action cannot be undone.
        </p>
        <div className="flex gap-2">
          <button onClick={onCancel} className="flex-1 rounded-lg border py-2 text-sm" style={{ borderColor: "var(--surface-border)" }}>
            Cancel
          </button>
          <button onClick={onConfirm} className="flex-1 rounded-lg py-2 text-sm text-white bg-red-600">
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}