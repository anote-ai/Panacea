import React, { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useAuth, useTheme } from "../App";
import RocketLogo from "../components/RocketLogo";
import StatusNotice from "../components/StatusNotice";
import { deleteSession, getSession, getSessions, streamChat } from "../api";
import { useServiceHealth } from "../hooks/useServiceHealth";
import {
  getChatStatusNotice,
  getEmptyStateSuggestions,
  getProviderLabel,
  getProviderForModel,
  getWorkspaceStatusItems,
  isModelConfigured,
} from "../lib/productReadiness";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface Session {
  id: string;
  title: string;
  createdAt: string;
}

const MODELS = ["claude-sonnet-4-6", "claude-haiku-4-5-20251001", "gpt-4o", "gpt-4o-mini"];

const STATUS_ITEM_STYLES = {
  good: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-200",
  warning: "bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-200",
  error: "bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-200",
  neutral: "bg-gray-100 text-gray-700 dark:bg-[#262626] dark:text-gray-200",
} as const;

export default function ChatPage() {
  const { setToken } = useAuth();
  const { dark, toggle } = useTheme();
  const nav = useNavigate();
  const { health, healthState } = useServiceHealth();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [input, setInput] = useState("");
  const [model, setModel] = useState(MODELS[0]);
  const [streaming, setStreaming] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  const selectedProvider = getProviderForModel(model);
  const selectedProviderLabel = getProviderLabel(selectedProvider);
  const providerReady = isModelConfigured(health, model);
  const chatStatusNotice = getChatStatusNotice(healthState, health, model);
  const emptyStateSuggestions = getEmptyStateSuggestions();
  const workspaceStatusItems = getWorkspaceStatusItems(healthState, health, model);
  const selectedSession = sessions.find((session) => session.id === sessionId);
  const composerPlaceholder =
    healthState === "offline"
      ? "Start the local backend to begin chatting..."
      : !providerReady
        ? "Add a provider key or run Ollama locally, then ask for a summary or status update..."
        : "Ask for a summary, risk review, or work report draft...";

  const loadSessions = useCallback(async () => {
    try {
      setSessions(await getSessions());
    } catch {}
  }, []);

  const loadMessages = useCallback(async (id: string) => {
    try {
      setMessages(await getSession(id));
    } catch {}
  }, []);

  useEffect(() => {
    loadSessions();
  }, [loadSessions]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (healthState !== "online" || providerReady) return;
    const fallback = MODELS.find((entry) => isModelConfigured(health, entry));
    if (fallback && fallback !== model) {
      setModel(fallback);
    }
  }, [health, healthState, model, providerReady]);

  const autoResize = () => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 200)}px`;
  };

  const focusComposer = () => {
    requestAnimationFrame(() => {
      textareaRef.current?.focus();
      autoResize();
    });
  };

  const openSession = async (id: string) => {
    setSessionId(id);
    await loadMessages(id);
  };

  const newChat = () => {
    setSessionId(null);
    setMessages([]);
    focusComposer();
  };

  const logout = () => {
    setToken(null);
    nav("/login", { replace: true });
  };

  const applySuggestedPrompt = (prompt: string) => {
    setInput(prompt);
    focusComposer();
  };

  const sendMessage = async () => {
    if (!input.trim() || streaming || healthState === "offline") return;
    const text = input.trim();
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    if (textareaRef.current) textareaRef.current.style.height = "auto";
    setStreaming(true);
    let assistantContent = "";
    let didAbort = false;
    let didReceiveText = false;
    let finalErrorMessage: string | null = null;
    setMessages((prev) => [...prev, { role: "assistant", content: "" }]);

    abortRef.current = new AbortController();
    try {
      await streamChat(
        text,
        sessionId,
        model,
        (chunk) => {
          didReceiveText = true;
          assistantContent += chunk;
          const content = assistantContent;
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = { role: "assistant", content };
            return updated;
          });
        },
        (id) => {
          setSessionId(id);
          loadSessions();
        },
        abortRef.current.signal,
      );
    } catch (e: any) {
      if (e.name !== "AbortError") {
        finalErrorMessage = e.message || "Sorry, something went wrong.";
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: "assistant", content: finalErrorMessage! };
          return updated;
        });
      } else {
        didAbort = true;
        if (!assistantContent) {
          setMessages((prev) => prev.slice(0, -1));
        }
      }
    } finally {
      if (!didReceiveText && !didAbort && !finalErrorMessage) {
        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: "No response was returned. Please verify your model configuration and try again.",
          };
          return updated;
        });
      }
      setStreaming(false);
      abortRef.current = null;
      loadSessions();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const doDeleteSession = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await deleteSession(id);
    if (sessionId === id) newChat();
    loadSessions();
  };

  return (
    <div className="flex h-screen bg-white text-gray-900 dark:bg-[#212121] dark:text-white">
      <aside
        className={`${
          sidebarOpen ? "w-72" : "w-0"
        } flex-shrink-0 overflow-hidden border-r border-gray-200 bg-[#F7F7F8] transition-all duration-200 dark:border-gray-800 dark:bg-[#171717]`}
      >
        <div className="flex h-full flex-col">
          <div className="border-b border-gray-200 dark:border-gray-800">
            <div className="p-3 pb-2">
              <div className="flex items-center gap-3">
                <div className="rounded-2xl bg-white p-2 shadow-sm dark:bg-[#202020]">
                  <RocketLogo className="h-7 w-7 flex-shrink-0" />
                </div>
                <div className="min-w-0">
                  <p className="text-[11px] uppercase tracking-[0.22em] text-gray-400 dark:text-gray-500">
                    Private desktop
                  </p>
                  <span className="block truncate text-sm font-semibold">Anote AI</span>
                </div>
              </div>
            </div>
            <div className="px-3 pb-3">
              <button
                onClick={newChat}
                className="w-full rounded-xl bg-gray-900 px-3 py-2.5 text-left text-sm font-medium text-white transition-colors hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100"
              >
                + New chat
              </button>
              <p className="mt-2 text-xs text-gray-400 dark:text-gray-500">
                {sessions.length} saved conversation{sessions.length === 1 ? "" : "s"}
              </p>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
            {sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => openSession(session.id)}
                className={`group flex cursor-pointer items-center justify-between rounded-xl px-3 py-2.5 text-sm transition-colors ${
                  session.id === sessionId
                    ? "bg-white shadow-sm dark:bg-[#222222]"
                    : "hover:bg-gray-200 dark:hover:bg-[#232323]"
                }`}
              >
                <span className="truncate">{session.title || "New chat"}</span>
                <button
                  onClick={(e) => doDeleteSession(session.id, e)}
                  className="ml-2 text-xs text-gray-400 opacity-0 transition hover:text-red-500 group-hover:opacity-100"
                >
                  ✕
                </button>
              </div>
            ))}
          </div>

          <div className="border-t border-gray-200 px-3 py-3 dark:border-gray-800">
            <div className="mb-3 space-y-1">
              <p className="text-[11px] uppercase tracking-[0.22em] text-gray-400 dark:text-gray-500">
                Local mode
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                On-device history, private previews, and desktop-first workflow review.
              </p>
            </div>
            <button
              onClick={logout}
              className="w-full rounded-xl px-3 py-2 text-left text-sm text-gray-600 transition-colors hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-[#232323]"
            >
              Sign out
            </button>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center justify-between gap-3 px-4 py-3">
            <div className="flex min-w-0 items-center gap-3">
              <button
                onClick={() => setSidebarOpen((open) => !open)}
                className="rounded-xl p-2 text-gray-500 transition-colors hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-[#2A2A2A]"
              >
                ☰
              </button>
              <div className="min-w-0">
                <p className="text-[11px] uppercase tracking-[0.22em] text-gray-400 dark:text-gray-500">
                  Workspace
                </p>
                <h1 className="truncate text-sm font-semibold text-gray-900 dark:text-white">
                  {selectedSession?.title || "New chat"}
                </h1>
              </div>
            </div>

            <div className="hidden items-center gap-2 lg:flex">
              <span className="rounded-full border border-gray-200 px-2.5 py-1 text-xs text-gray-500 dark:border-gray-700 dark:text-gray-300">
                Private desktop
              </span>
              <span
                className={`rounded-full px-2.5 py-1 text-xs ${
                  STATUS_ITEM_STYLES[healthState === "online" ? "good" : healthState === "offline" ? "error" : "neutral"]
                }`}
              >
                {healthState === "online" ? "Backend online" : healthState === "offline" ? "Backend offline" : "Checking backend"}
              </span>
              <span
                className={`rounded-full px-2.5 py-1 text-xs ${
                  STATUS_ITEM_STYLES[providerReady ? "good" : "warning"]
                }`}
              >
                {providerReady ? "Model ready" : "Model setup needed"}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="rounded-xl border border-gray-300 bg-transparent px-3 py-1.5 text-sm text-gray-700 focus:outline-none dark:border-gray-600 dark:text-gray-300"
              >
                {MODELS.map((entry) => (
                  <option key={entry} value={entry}>
                    {entry}
                  </option>
                ))}
              </select>
              <button
                onClick={toggle}
                className="rounded-xl p-2 text-gray-500 transition-colors hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-[#2A2A2A]"
              >
                {dark ? "☀️" : "🌙"}
              </button>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 px-4 pb-3 lg:hidden">
            <span className="rounded-full border border-gray-200 px-2.5 py-1 text-xs text-gray-500 dark:border-gray-700 dark:text-gray-300">
              Private desktop
            </span>
            <span
              className={`rounded-full px-2.5 py-1 text-xs ${
                STATUS_ITEM_STYLES[healthState === "online" ? "good" : healthState === "offline" ? "error" : "neutral"]
              }`}
            >
              {healthState === "online" ? "Backend online" : healthState === "offline" ? "Backend offline" : "Checking backend"}
            </span>
            <span
              className={`rounded-full px-2.5 py-1 text-xs ${
                STATUS_ITEM_STYLES[providerReady ? "good" : "warning"]
              }`}
            >
              {providerReady ? "Model ready" : "Model setup needed"}
            </span>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex min-h-full items-center">
              <div className="stage-enter mx-auto w-full max-w-5xl px-6 py-10">
                {chatStatusNotice && <StatusNotice notice={chatStatusNotice} className="mb-6 max-w-2xl" />}

                <div className="space-y-4">
                  <div className="flex flex-wrap gap-2 text-[11px] uppercase tracking-[0.22em] text-gray-400 dark:text-gray-500">
                    <span className="rounded-full border border-gray-200 px-3 py-1 dark:border-gray-700">
                      Local-first workspace
                    </span>
                    <span className="rounded-full border border-gray-200 px-3 py-1 dark:border-gray-700">
                      {sessions.length} saved chat{sessions.length === 1 ? "" : "s"}
                    </span>
                    <span className="rounded-full border border-gray-200 px-3 py-1 dark:border-gray-700">
                      {providerReady ? `${selectedProviderLabel} ready` : `${selectedProviderLabel} setup needed`}
                    </span>
                  </div>

                  <h2 className="max-w-3xl text-3xl font-semibold tracking-tight text-gray-900 dark:text-white md:text-5xl">
                    Private workspace for summaries, risks, and status updates.
                  </h2>

                  <p className="max-w-2xl text-sm leading-7 text-gray-500 dark:text-gray-400 md:text-base">
                    Use the desktop app to review product changes, draft a work report, and keep your notes and chat
                    history local to this machine while you iterate.
                  </p>
                </div>

                <div className="mt-10 grid gap-10 lg:grid-cols-[minmax(0,1.7fr)_minmax(260px,0.95fr)]">
                  <section className="space-y-5">
                    <div className="space-y-3">
                      <p className="text-[11px] uppercase tracking-[0.22em] text-gray-400 dark:text-gray-500">
                        Quick starts
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {emptyStateSuggestions.map((prompt) => (
                          <button
                            key={prompt}
                            onClick={() => applySuggestedPrompt(prompt)}
                            className="rounded-full border border-gray-200 px-4 py-2 text-left text-sm text-gray-700 transition hover:-translate-y-0.5 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-[#262626]"
                          >
                            {prompt}
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-2 text-sm">
                      <button
                        onClick={focusComposer}
                        className="rounded-full bg-gray-900 px-4 py-2 text-white transition hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100"
                      >
                        Start typing
                      </button>
                      <span className="rounded-full border border-gray-200 px-3 py-2 text-gray-500 dark:border-gray-700 dark:text-gray-400">
                        Selected model: {model}
                      </span>
                    </div>
                  </section>

                  <aside className="space-y-4 lg:border-l lg:border-gray-200 lg:pl-8 dark:lg:border-gray-800">
                    <p className="text-[11px] uppercase tracking-[0.22em] text-gray-400 dark:text-gray-500">
                      Workspace status
                    </p>
                    <div className="space-y-4">
                      {workspaceStatusItems.map((item) => (
                        <div key={item.label} className="space-y-1.5">
                          <div className="flex items-center justify-between gap-3">
                            <span className="text-sm font-medium text-gray-800 dark:text-gray-100">{item.label}</span>
                            <span className={`rounded-full px-2.5 py-1 text-xs ${STATUS_ITEM_STYLES[item.tone]}`}>
                              {item.value}
                            </span>
                          </div>
                          <p className="text-sm leading-6 text-gray-500 dark:text-gray-400">{item.detail}</p>
                        </div>
                      ))}
                    </div>
                  </aside>
                </div>
              </div>
            </div>
          ) : (
            <div className="mx-auto w-full max-w-4xl px-4 py-6">
              {chatStatusNotice && <StatusNotice notice={chatStatusNotice} className="mb-6" />}
              <div className="space-y-6">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex gap-4 ${message.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {message.role === "assistant" && (
                      <div className="mt-0.5 flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-gray-100 dark:bg-[#2F2F2F]">
                        <RocketLogo className="h-5 w-5" />
                      </div>
                    )}
                    <div
                      className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                        message.role === "user"
                          ? "bg-gray-100 dark:bg-[#2F2F2F]"
                          : "border border-transparent bg-transparent"
                      }`}
                    >
                      {message.role === "assistant" ? (
                        <div className="prose prose-sm max-w-none dark:prose-invert">
                          <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {message.content || (streaming && index === messages.length - 1 ? "▋" : "")}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <p className="whitespace-pre-wrap text-sm">{message.content}</p>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            </div>
          )}
        </div>

        <div className="border-t border-gray-200 px-4 py-4 dark:border-gray-800">
          <div className="mx-auto max-w-4xl">
            <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
              <p className="text-[11px] uppercase tracking-[0.22em] text-gray-400 dark:text-gray-500">
                Private composer
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500">
                {healthState === "offline"
                  ? "Backend offline"
                  : providerReady
                    ? `${selectedProviderLabel} ready for local chat`
                    : `${selectedProviderLabel} setup needed for this model`}
              </p>
            </div>
            <div className="relative flex items-end rounded-2xl border border-gray-300 bg-[#F7F7F8] dark:border-gray-600 dark:bg-[#2F2F2F]">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  autoResize();
                }}
                onKeyDown={handleKeyDown}
                placeholder={composerPlaceholder}
                rows={1}
                className="min-h-[52px] flex-1 bg-transparent px-4 py-3.5 text-sm text-gray-900 placeholder-gray-400 focus:outline-none dark:text-white dark:placeholder-gray-500"
              />
              <button
                onClick={streaming ? () => abortRef.current?.abort() : sendMessage}
                disabled={!streaming && (!input.trim() || healthState === "offline")}
                className="m-2 flex-shrink-0 rounded-xl bg-gray-900 p-2 text-white transition-colors hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-30 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100"
              >
                {streaming ? (
                  <span className="flex h-4 w-4 items-center justify-center text-xs">■</span>
                ) : (
                  <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M2 21l21-9L2 3v7l15 2-15 2v7z" />
                  </svg>
                )}
              </button>
            </div>
            <p className="mt-2 text-center text-xs text-gray-400 dark:text-gray-500">
              All data stays private on your device.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
