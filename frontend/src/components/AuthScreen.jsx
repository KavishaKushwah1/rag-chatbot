import { useState } from "react";
import { Sun, Moon } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

export default function AuthScreen() {
  const { signIn, signUp, signInWithGoogle } = useAuth();
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

        <div className="flex items-center gap-3 my-4">
          <div className="flex-1 border-t" style={{ borderColor: "var(--surface-border)" }} />
          <span className="text-xs" style={{ color: "var(--muted)" }}>or</span>
          <div className="flex-1 border-t" style={{ borderColor: "var(--surface-border)" }} />
        </div>

        <button
          onClick={signInWithGoogle}
          className="w-full flex items-center justify-center gap-2 rounded-lg border py-2.5 text-sm font-medium transition-colors hover:bg-[var(--accent-soft)]"
          style={{ borderColor: "var(--surface-border)", background: "var(--input-bg)" }}
        >
          <svg width="18" height="18" viewBox="0 0 18 18">
            <path fill="#4285F4" d="M17.64 9.2c0-.64-.06-1.25-.16-1.84H9v3.48h4.84a4.14 4.14 0 0 1-1.8 2.72v2.26h2.92c1.7-1.57 2.68-3.88 2.68-6.62z" />
            <path fill="#34A853" d="M9 18c2.43 0 4.47-.8 5.96-2.18l-2.92-2.26c-.81.54-1.84.86-3.04.86-2.34 0-4.32-1.58-5.03-3.7H.96v2.33A9 9 0 0 0 9 18z" />
            <path fill="#FBBC05" d="M3.97 10.72A5.4 5.4 0 0 1 3.68 9c0-.6.1-1.18.29-1.72V4.95H.96A9 9 0 0 0 0 9c0 1.45.35 2.83.96 4.05l3.01-2.33z" />
            <path fill="#EA4335" d="M9 3.58c1.32 0 2.51.45 3.44 1.35l2.59-2.59C13.46.89 11.43 0 9 0A9 9 0 0 0 .96 4.95l3.01 2.33C4.68 5.16 6.66 3.58 9 3.58z" />
          </svg>
          Continue with Google
        </button>

        {tab === "login" && (
          <div className="text-center text-xs mt-4" style={{ color: "var(--muted)" }}>
            Need an account? Contact your administrator.
          </div>
        )}
      </div>
    </div>
  );
}