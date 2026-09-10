import type { ReactNode } from "react";
import { useTheme } from "../App";
import OurogenWordmark from "./OurogenWordmark";

export default function AuthLayout({ title, description, children }: {
  title: string;
  description: string;
  children: ReactNode;
}) {
  const { themeMode, setThemeMode } = useTheme();
  return (
    <div className="min-h-dvh flex flex-col bg-white dark:bg-black text-gray-900 dark:text-white">
      <header className="flex items-center justify-between gap-4 px-5 py-5 sm:px-8">
        <a href="https://ourogen.ai" aria-label="Ourogen home"><OurogenWordmark imgHeight="h-8" /></a>
        <select aria-label="Appearance" value={themeMode} onChange={(event) => setThemeMode(event.target.value as typeof themeMode)}
          className="rounded-xl border border-gray-200 dark:border-gray-800 bg-transparent px-3 py-2 text-sm">
          <option value="system">System theme</option>
          <option value="light">Light theme</option>
          <option value="dark">Dark theme</option>
        </select>
      </header>
      <main className="flex flex-1 items-center justify-center px-5 py-10 sm:py-16">
        <div className="w-full max-w-md rounded-2xl border border-gray-200 dark:border-gray-800 p-6 sm:p-8">
          <div className="mb-8">
            <p className="eyebrow text-gray-500 dark:text-gray-400">Ourogen Chat</p>
            <h1 className="mt-3 text-3xl font-semibold tracking-tight">{title}</h1>
            <p className="mt-3 text-sm leading-6 text-gray-600 dark:text-gray-400">{description}</p>
          </div>
          {children}
        </div>
      </main>
      <footer className="flex flex-wrap justify-center gap-x-6 gap-y-2 px-5 pb-6 text-sm text-gray-600 dark:text-gray-400">
        <a href="https://docs.ourogen.ai" className="hover:underline">Documentation</a>
        <a href="https://ourogen.ai/products" className="hover:underline">Explore products</a>
      </footer>
    </div>
  );
}
