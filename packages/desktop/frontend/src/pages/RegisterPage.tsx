import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth, useTheme } from "../App";
import OurogenLogo from "../components/OurogenLogo";
import { register } from "../api";

export default function RegisterPage() {
  const { setToken } = useAuth();
  const { dark, toggle } = useTheme();
  const nav = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      const token = await register(email, password, name);
      setToken(token); nav("/");
    } catch (err: any) {
      setError(err.response?.data?.error || "Registration failed");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-20 bg-white dark:bg-[#212121]">
      <button onClick={toggle} aria-label="Toggle appearance" className="absolute top-4 right-4 p-2 rounded-xl text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-[#2F2F2F]">
        {dark ? "Light" : "Dark"}
      </button>
      <div className="w-full max-w-md mx-5 p-8 rounded-2xl border border-gray-200 dark:border-gray-700">
        <div className="flex flex-col items-center mb-8">
          <OurogenLogo className="w-12 h-12 mb-4" />
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Create account</h1>
        </div>
        <form onSubmit={submit} className="space-y-4">
          <label htmlFor="text" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Name (optional)</label>
          <input id="text" autoComplete="name" type="text" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#2F2F2F] text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-400" />
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Email address</label>
          <input id="email" autoComplete="email" type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} required
            className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#2F2F2F] text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-400" />
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
          <input id="password" autoComplete="new-password" type="password" placeholder="Password (min 8 chars)" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8}
            className="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#2F2F2F] text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-400" />
          {error && <p role="alert" className="text-red-600 dark:text-red-400 text-sm">{error}</p>}
          <button type="submit" disabled={loading}
            className="w-full py-3 rounded-xl bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-medium hover:bg-gray-800 dark:hover:bg-gray-100 disabled:opacity-50 transition-colors">
            {loading ? "Creating..." : "Create account"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
          Have an account? <Link to="/login" className="text-gray-900 dark:text-white font-medium hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
