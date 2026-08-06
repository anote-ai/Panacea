import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth, useTheme } from "../App";
import RocketLogo from "../components/RocketLogo";
import StatusNotice from "../components/StatusNotice";
import { useServiceHealth } from "../hooks/useServiceHealth";
import { getAuthStatusNotice } from "../lib/productReadiness";
import { login } from "../api";

export default function LoginPage() {
  const { setToken } = useAuth();
  const { dark, toggle } = useTheme();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { health, healthState } = useServiceHealth();
  const readinessNotice = getAuthStatusNotice(healthState, health);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      const token = await login(email, password);
      setToken(token);
      nav("/", { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.error || "Login failed");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white dark:bg-[#212121]">
      <button onClick={toggle} className="absolute top-4 right-4 p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-[#2F2F2F]">
        {dark ? "☀️" : "🌙"}
      </button>
      <div className="w-full max-w-md px-8">
        <div className="mb-8 space-y-4">
          <div className="flex flex-col items-center text-center">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-gray-200 bg-gray-50 px-3 py-1 text-[11px] uppercase tracking-[0.2em] text-gray-500 dark:border-gray-700 dark:bg-[#1D1D1D] dark:text-gray-400">
              <span className="inline-flex h-2 w-2 rounded-full bg-emerald-500" />
              Private desktop
            </div>
            <RocketLogo className="w-12 h-12 mb-4" />
            <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Welcome back</h1>
            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
              Review risks, draft status updates, and keep the workspace local to this device.
            </p>
          </div>
          {readinessNotice && <StatusNotice notice={readinessNotice} />}
        </div>
        <form onSubmit={submit} className="space-y-4">
          <input type="email" name="email" autoComplete="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required
            className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#2F2F2F] text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-400" />
          <input type="password" name="password" autoComplete="current-password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required
            className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#2F2F2F] text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-400" />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit" disabled={loading || healthState === "offline"}
            className="w-full py-3 rounded-lg bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-medium hover:bg-gray-800 dark:hover:bg-gray-100 disabled:opacity-50 transition-colors">
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
          No account? <Link to="/register" className="text-gray-900 dark:text-white font-medium hover:underline">Create one</Link>
        </p>
      </div>
    </div>
  );
}
