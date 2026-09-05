import { AlertTriangle } from "lucide-react";

export default function WarningCard({ children }) {
  return (
    <div
      className="flex items-center gap-2 rounded-lg border px-3 py-2 text-sm my-2"
      style={{ background: "var(--warning-bg)", borderColor: "var(--warning-border)", color: "var(--warning-text)" }}
    >
      <AlertTriangle size={16} />
      <span>{children}</span>
    </div>
  );
}