import React, { useEffect, useState } from "react";
import { getProviderKeys, setProviderKey, deleteProviderKey } from "../api";

interface Props {
  open: boolean;
  onClose: () => void;
}

const PROVIDERS: { id: string; label: string }[] = [
  { id: "anthropic", label: "Anthropic (Claude)" },
  { id: "openai", label: "OpenAI (GPT)" },
  { id: "google", label: "Google (Gemini)" },
];

export default function SettingsModal({ open, onClose }: Props) {
  const [keys, setKeys] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [inputs, setInputs] = useState<Record<string, string>>({});
  const [openProvider, setOpenProvider] = useState<string | null>(null);
  const [saving, setSaving] = useState<Record<string, boolean>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!open) return;
    setInputs({});
    setOpenProvider(null);
    setErrors({});
    setLoading(true);
    getProviderKeys()
      .then(setKeys)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [open]);

  if (!open) return null;

  const save = async (provider: string) => {
    const key = (inputs[provider] || "").trim();
    if (!key) return;
    setSaving((s) => ({ ...s, [provider]: true }));
    setErrors((e) => ({ ...e, [provider]: "" }));
    try {
      const masked = await setProviderKey(provider, key);
      setKeys((k) => ({ ...k, [provider]: masked }));
      setInputs((i) => ({ ...i, [provider]: "" }));
      setOpenProvider(null);
    } catch (err: any) {
      setErrors((e) => ({ ...e, [provider]: err.response?.data?.error || "Failed to save key" }));
    } finally {
      setSaving((s) => ({ ...s, [provider]: false }));
    }
  };

  const remove = async (provider: string) => {
    setErrors((e) => ({ ...e, [provider]: "" }));
    try {
      await deleteProviderKey(provider);
      setKeys((k) => { const next = { ...k }; delete next[provider]; return next; });
      setOpenProvider(null);
    } catch (err: any) {
      setErrors((e) => ({ ...e, [provider]: err.response?.data?.error || "Failed to remove key" }));
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4" onClick={onClose}>
      <div
        className="bg-white dark:bg-[#2F2F2F] rounded-2xl shadow-xl w-full max-w-md max-h-[85vh] flex flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-base font-semibold text-gray-900 dark:text-white">API keys</h3>
          <button
            onClick={onClose}
            aria-label="Close"
            className="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-[#3F3F3F] transition-colors"
          >
            ✕
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-5 py-4">
          <p className="text-xs text-gray-400 dark:text-gray-500 mb-4">
            Bring your own provider keys — they're encrypted and stored on this device, and used
            for your chats instead of the shared default.
          </p>
          {loading ? (
            <p className="text-xs text-gray-400 dark:text-gray-500">Loading…</p>
          ) : (
            <div className="space-y-2">
              {PROVIDERS.map((p) => {
                const isSet = !!keys[p.id];
                const isOpen = openProvider === p.id;
                return (
                  <div key={p.id}>
                    <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-[#F7F7F8] dark:bg-[#1a1a1a]">
                      <span className="text-sm text-gray-700 dark:text-gray-300">{p.label}</span>
                      <div className="flex items-center gap-2">
                        <span className={`text-xs ${isSet ? "text-green-600 dark:text-green-400" : "text-gray-400 dark:text-gray-500"}`}>
                          {isSet ? keys[p.id] : "Not set"}
                        </span>
                        <button
                          onClick={() => setOpenProvider(isOpen ? null : p.id)}
                          className="text-xs text-gray-600 dark:text-gray-300 hover:underline"
                        >
                          {isOpen ? "Cancel" : isSet ? "Edit" : "Set"}
                        </button>
                      </div>
                    </div>
                    {isOpen && (
                      <div className="mt-2">
                        <div className="flex items-center gap-2">
                          <input
                            type="password"
                            autoFocus
                            value={inputs[p.id] || ""}
                            onChange={(e) => setInputs((i) => ({ ...i, [p.id]: e.target.value }))}
                            onKeyDown={(e) => { if (e.key === "Enter") save(p.id); }}
                            placeholder={isSet ? "Replace key…" : "Enter API key…"}
                            className="flex-1 bg-white dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-white focus:outline-none"
                          />
                          <button
                            onClick={() => save(p.id)}
                            disabled={saving[p.id] || !inputs[p.id]?.trim()}
                            className="px-3 py-2 rounded-lg text-sm bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                          >
                            Save
                          </button>
                          {isSet && (
                            <button onClick={() => remove(p.id)} className="px-2 py-2 text-xs text-red-500 hover:text-red-600">
                              Remove
                            </button>
                          )}
                        </div>
                        {errors[p.id] && <p className="text-xs text-red-500 mt-1">{errors[p.id]}</p>}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
