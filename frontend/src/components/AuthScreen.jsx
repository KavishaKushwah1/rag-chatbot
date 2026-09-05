import { useState } from "react";
import { Sun, Moon } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

export default function AuthScreen() {
  const { signIn, signUp } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [tab, setTab] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  async function handleLogin(e) {
    e.preventDefault();
    setError(""); setInfo("");
    const { error } = await signIn(email, password);
    if (error) setError(error.message);
  }

  async function handleSignup(e) {
    e.preventDefault();
    setError(""); setInfo("");
    const { error } = await signUp(email, password);
    if (error) setError(error.message);
    else setInfo("Account created. You can now log in.");
  }

  return (
    <div className="min-h-screen flex flex-col items-center pt-10 px-4" style={{ background: "var(--bg)" }}>
      <button onClick={toggleTheme} className="self-end mb-6 p-2 rounded-lg border" style={{ borderColor: "var(--surface-border)" }}>
        {theme === "light" ? <Moon size={16} /> : <Sun size={16} />}
      </button>

      <div className="text-center mb-8">
        <div className="text-3xl font-semibold tracking-tight">Acme</div>
        <div className="text-lg font-medium -mt-1">Knowledge Assistant</div>
        <div className="text-sm mt-2" style={{ color: "var(--muted)" }}>Your company knowledge, at your fingertips.</div>
      </div>

      <div className="w-full max-w-sm rounded-xl border p-6" style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)" }}>
        <div className="flex gap-6 mb-5 text-sm font-medium border-b" style={{ borderColor: "var(--surface-border)" }}>
          {["login", "signup"].map((t) => (
            <button
              key={t}
              onClick={() => { setTab(t); setError(""); setInfo(""); }}
              className="pb-2 -mb-px"
              style={{
                color: tab === t ? "var(--accent)" : "var(--muted)",
                borderBottom: tab === t ? "2px solid var(--accent)" : "2px solid transparent",
              }}
            >
              {t === "login" ? "Log in" : "Sign up"}
            </button>
          ))}
        </div>

        <form onSubmit={tab === "login" ? handleLogin : handleSignup} className="flex flex-col gap-4">
          <div>
            <label className="text-sm font-medium">Email</label>
            <input
              type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              placeholder="you@acme.com"
              className="w-full mt-1 rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2"
              style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)", color: "var(--text)" }}
            />
          </div>
          <div>
            <label className="text-sm font-medium">Password</label>
            <input
              type="password" required value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full mt-1 rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2"
              style={{ background: "var(--input-bg)", borderColor: "var(--surface-border)", color: "var(--text)" }}
            />
            {tab === "login" && (
              <div className="text-right text-xs mt-1" style={{ color: "var(--muted)" }}>Forgot password?</div>
            )}
          </div>

          {error && <div className="text-sm text-red-500">{error}</div>}
          {info && <div className="text-sm text-green-600">{info}</div>}

          <button
            type="submit"
            className="w-full rounded-lg py-2 text-sm font-medium text-white"
            style={{ background: "var(--accent)" }}
          >
            {tab === "login" ? "Log in" : "Create account"}
          </button>
        </form>

        {tab === "login" && (
          <div className="text-center text-xs mt-4" style={{ color: "var(--muted)" }}>
            Need an account? Contact your administrator.
          </div>
        )}
      </div>
    </div>
  );
}