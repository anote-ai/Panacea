import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import { GoogleLogin, CredentialResponse } from "@react-oauth/google";
import { useAuth, useTheme } from "../App";
import AnoteWordmark from "../components/AnoteWordmark";

export default function LoginPage() {
  const { setToken } = useAuth();
  const { dark, toggle } = useTheme();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await axios.post("/auth/login", { email, password });
      setToken(res.data.token);
      nav("/app");
    } catch (err: any) {
      setError(err.response?.data?.error || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    setError("");
    if (!credentialResponse.credential) {
      setError("Google sign-in failed");
      return;
    }
    setLoading(true);
    try {
      const res = await axios.post("/auth/google", { credential: credentialResponse.credential });
      setToken(res.data.token);
      nav("/app");
    } catch (err: any) {
      setError(err.response?.data?.error || "Google sign-in failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white dark:bg-[#212121]">
      <button
        onClick={toggle}
        className="absolute top-4 right-4 p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-[#2F2F2F]"
        aria-label="Toggle theme"
      >
        {dark ? "☀️" : "🌙"}
      </button>
      <div className="w-full max-w-sm px-8">
        <div className="flex flex-col items-center mb-8">
          <AnoteWordmark className="mb-4" />
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Welcome back</h1>
        </div>
        <div className="flex justify-center mb-6">
          <GoogleLogin
            onSuccess={handleGoogleSuccess}
            onError={() => setError("Google sign-in failed")}
            theme={dark ? "filled_black" : "outline"}
            width="320"
          />
        </div>
        <div className="flex items-center gap-3 mb-6">
          <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700" />
          <span className="text-xs text-gray-400 dark:text-gray-500">OR</span>
          <div className="h-px flex-1 bg-gray-200 dark:bg-gray-700" />
        </div>
        <form onSubmit={submit} className="space-y-4">
          <div>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#2F2F2F] text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-400 dark:focus:ring-gray-500"
            />
          </div>
          <div>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#2F2F2F] text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-gray-400 dark:focus:ring-gray-500"
            />
          </div>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-lg bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-medium hover:bg-gray-800 dark:hover:bg-gray-100 disabled:opacity-50 transition-colors"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
          Don't have an account?{" "}
          <Link to="/register" className="text-gray-900 dark:text-white font-medium hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
