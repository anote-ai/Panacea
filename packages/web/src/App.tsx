import axios from "axios";
import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ChatPage from "./pages/ChatPage";
import DocumentsPage from "./pages/DocumentsPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";

// Theme
export type ThemeMode = "light" | "dark" | "system";

export const ThemeContext = createContext<{
  dark: boolean;
  themeMode: ThemeMode;
  setThemeMode: (m: ThemeMode) => void;
  toggle: () => void;
}>({ dark: false, themeMode: "system", setThemeMode: () => {}, toggle: () => {} });

// Auth
export interface UserProfile {
  name: string;
  email: string;
  hasAvatar: boolean;
}

export const AuthContext = createContext<{
  token: string | null;
  setToken: (t: string | null) => void;
  user: UserProfile | null;
  refreshUser: () => void;
  avatarVersion: number;
  bumpAvatarVersion: () => void;
}>({
  token: null,
  setToken: () => {},
  user: null,
  refreshUser: () => {},
  avatarVersion: 0,
  bumpAvatarVersion: () => {},
});

export function useTheme() { return useContext(ThemeContext); }
export function useAuth() { return useContext(AuthContext); }

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { token } = useAuth();
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  const [themeMode, setThemeModeState] = useState<ThemeMode>(() => {
    const stored = localStorage.getItem("themeMode");
    if (stored === "light" || stored === "dark" || stored === "system") return stored;
    // Migrate the old boolean-only "theme" key from before System mode existed.
    const legacy = localStorage.getItem("theme");
    if (legacy === "light" || legacy === "dark") return legacy;
    return "system";
  });
  const [systemDark, setSystemDark] = useState(
    () => window.matchMedia("(prefers-color-scheme: dark)").matches
  );

  const [token, setTokenState] = useState<string | null>(
    () => localStorage.getItem("token")
  );
  const [user, setUser] = useState<UserProfile | null>(null);
  const [avatarVersion, setAvatarVersion] = useState(0);

  const dark = themeMode === "system" ? systemDark : themeMode === "dark";

  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const handler = (e: MediaQueryListEvent) => setSystemDark(e.matches);
    mq.addEventListener("change", handler);
    return () => mq.removeEventListener("change", handler);
  }, []);

  useEffect(() => {
    if (dark) document.documentElement.classList.add("dark");
    else document.documentElement.classList.remove("dark");
  }, [dark]);

  const setThemeMode = (m: ThemeMode) => {
    setThemeModeState(m);
    localStorage.setItem("themeMode", m);
  };
  const toggle = () => setThemeMode(dark ? "light" : "dark");
  const setToken = (t: string | null) => {
    setTokenState(t);
    if (t) localStorage.setItem("token", t);
    else localStorage.removeItem("token");
  };

  const refreshUser = useCallback(async () => {
    if (!token) {
      setUser(null);
      return;
    }
    try {
      const res = await axios.get("/api/user/profile", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser({
        name: res.data.name || "",
        email: res.data.email || "",
        hasAvatar: !!res.data.hasAvatar,
      });
    } catch {
      setUser(null);
    }
  }, [token]);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const bumpAvatarVersion = () => setAvatarVersion((v) => v + 1);

  return (
    <ThemeContext.Provider value={{ dark, themeMode, setThemeMode, toggle }}>
      <AuthContext.Provider
        value={{ token, setToken, user, refreshUser, avatarVersion, bumpAvatarVersion }}
      >
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/app" element={<RequireAuth><ChatPage /></RequireAuth>} />
            <Route path="/app/chat/:id" element={<RequireAuth><ChatPage /></RequireAuth>} />
            <Route path="/documents" element={<RequireAuth><DocumentsPage /></RequireAuth>} />
          </Routes>
        </BrowserRouter>
      </AuthContext.Provider>
    </ThemeContext.Provider>
  );
}
