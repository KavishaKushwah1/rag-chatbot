const SUBTEXTS = [
  "Ask about HR policies, engineering docs, product plans, or anything else at Acme.",
  "Every answer is grounded in a cited source document.",
  "Pick up where you left off, or start something new.",
];

function timeGreeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

export default function EmptyState({ displayName }) {
  const subtext = SUBTEXTS[Math.floor(Math.random() * SUBTEXTS.length)];
  return (
    <div className="text-center py-16 px-4">
      <div className="text-3xl font-semibold">{timeGreeting()}, {displayName || "there"}</div>
      <div className="text-lg mt-1">What would you like to know today?</div>
      <div className="text-sm mt-2 max-w-md mx-auto" style={{ color: "var(--muted)" }}>{subtext}</div>
    </div>
  );
}