import React, { createContext, useContext, useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ChatPage from "./pages/ChatPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import { setCachedToken, setUnauthorizedHandler } from "./api";
import { loadToken, saveToken } from "./auth-storage";

export const ThemeContext = createContext<{ dark: boolean; toggle: () => void }>({ dark: false, toggle: () => {} });
export const AuthContext = createContext<{ token: string | null; setToken: (t: string | null) => void }>({ token: null, setToken: () => {} });

export function useTheme() { return useContext(ThemeContext); }
export function useAuth() { return useContext(AuthContext); }

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { token } = useAuth();
  return token ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  const [dark, setDark] = useState(() => {
    const s = localStorage.getItem("theme");
    return s ? s === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
  });
  const [token, setTokenState] = useState<string | null>(null);
  const [authReady, setAuthReady] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  const setToken = (t: string | null) => {
    setTokenState(t);
    setCachedToken(t);
    saveToken(t);
  };

  useEffect(() => {
    let cancelled = false;
    loadToken().then((t) => {
      if (cancelled) return;
      setCachedToken(t);
      setTokenState(t);
      setAuthReady(true);
    });
    return () => { cancelled = true; };
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(() => setToken(null));
    return () => setUnauthorizedHandler(null);
  }, []);

  if (!authReady) {
    return <div className="min-h-screen bg-white dark:bg-[#212121]" />;
  }

  return (
    <ThemeContext.Provider value={{ dark, toggle: () => setDark((d) => !d) }}>
      <AuthContext.Provider value={{ token, setToken }}>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/*" element={<RequireAuth><ChatPage /></RequireAuth>} />
          </Routes>
        </BrowserRouter>
      </AuthContext.Provider>
    </ThemeContext.Provider>
  );
}
