import axios from 'axios';
import { useEffect, useRef, useState } from 'react';
import { type ThemeMode, useAuth, useModel, useTheme } from '../App';
import { MODELS } from '../constants/models';
import UserAvatar from './UserAvatar';

interface Props {
  open: boolean;
  onClose: () => void;
}

type Section = 'general' | 'account' | 'apiUsage' | 'display' | 'billing';

const NAV_ITEMS: { id: Section; label: string }[] = [
  { id: 'general', label: 'General' },
  { id: 'account', label: 'Account' },
  { id: 'apiUsage', label: 'API Usage' },
  { id: 'display', label: 'Display' },
  { id: 'billing', label: 'Billing' },
];

const PROVIDERS: { id: string; label: string }[] = [
  { id: 'anthropic', label: 'Anthropic (Claude)' },
  { id: 'openai', label: 'OpenAI (GPT)' },
  { id: 'google', label: 'Google (Gemini)' },
];

export default function SettingsModal({ open, onClose }: Props) {
  const { token, user, refreshUser, avatarVersion, bumpAvatarVersion } = useAuth();
  const { themeMode, setThemeMode } = useTheme();
  const { model, setModel } = useModel();
  const [section, setSection] = useState<Section>('general');
  const [name, setName] = useState(user?.name || '');
  const [saving, setSaving] = useState(false);
  const [avatarError, setAvatarError] = useState<string | null>(null);
  const [nameError, setNameError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [providerKeys, setProviderKeys] = useState<Record<string, string>>({});
  const [providerKeysLoading, setProviderKeysLoading] = useState(false);
  const [keyInputs, setKeyInputs] = useState<Record<string, string>>({});
  const [keyErrors, setKeyErrors] = useState<Record<string, string>>({});
  const [keySaving, setKeySaving] = useState<Record<string, boolean>>({});
  const [openProviders, setOpenProviders] = useState<Record<string, boolean>>({});

  const [billingLoading, setBillingLoading] = useState(false);
  const [billingError, setBillingError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      setSection('general');
      setName(user?.name || '');
      setAvatarError(null);
      setNameError(null);
      setKeyInputs({});
      setKeyErrors({});
      setOpenProviders({});
      setBillingError(null);
    }
  }, [open, user?.name]);

  useEffect(() => {
    if (open && section === 'apiUsage') {
      setProviderKeysLoading(true);
      axios
        .get('/api/user/provider-keys', { headers: { Authorization: `Bearer ${token}` } })
        .then((res) => setProviderKeys(res.data.keys || {}))
        .catch(() => {})
        .finally(() => setProviderKeysLoading(false));
    }
  }, [open, section, token]);

  const saveProviderKey = async (provider: string) => {
    const key = (keyInputs[provider] || '').trim();
    if (!key) return;
    setKeySaving((s) => ({ ...s, [provider]: true }));
    setKeyErrors((e) => ({ ...e, [provider]: '' }));
    try {
      const res = await axios.put(
        '/api/user/provider-keys',
        { provider, key },
        { headers: { Authorization: `Bearer ${token}` } },
      );
      setProviderKeys((keys) => ({ ...keys, [provider]: res.data.masked }));
      setKeyInputs((inputs) => ({ ...inputs, [provider]: '' }));
      setOpenProviders((open) => ({ ...open, [provider]: false }));
    } catch (err: any) {
      setKeyErrors((e) => ({
        ...e,
        [provider]: err?.response?.data?.error || err?.message || 'Failed to save key.',
      }));
    } finally {
      setKeySaving((s) => ({ ...s, [provider]: false }));
    }
  };

  const removeProviderKey = async (provider: string) => {
    setKeyErrors((e) => ({ ...e, [provider]: '' }));
    try {
      await axios.delete(`/api/user/provider-keys/${provider}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setProviderKeys((keys) => {
        const next = { ...keys };
        delete next[provider];
        return next;
      });
      setOpenProviders((open) => ({ ...open, [provider]: false }));
    } catch (err: any) {
      setKeyErrors((e) => ({
        ...e,
        [provider]: err?.response?.data?.error || err?.message || 'Failed to remove key.',
      }));
    }
  };

  const openBillingPortal = async () => {
    setBillingLoading(true);
    setBillingError(null);
    try {
      const res = await axios.post(
        '/api/payments/portal',
        { returnUrl: window.location.href },
        { headers: { Authorization: `Bearer ${token}` } },
      );
      window.location.href = res.data.url;
    } catch (err: any) {
      setBillingError(
        err?.response?.data?.error || err?.message || 'Billing is not configured yet.',
      );
    } finally {
      setBillingLoading(false);
    }
  };

  if (!open) return null;

  const uploadAvatar = async (file: File) => {
    setAvatarError(null);
    const form = new FormData();
    form.append('file', file);
    try {
      await axios.post('/api/user/avatar', form, {
        headers: { Authorization: `Bearer ${token}` },
      });
      bumpAvatarVersion();
      refreshUser();
    } catch (err: any) {
      setAvatarError(
        err?.response?.data?.error || err?.message || 'Upload failed — please try again.',
      );
    }
  };

  const removeAvatar = async () => {
    setAvatarError(null);
    try {
      await axios.delete('/api/user/avatar', { headers: { Authorization: `Bearer ${token}` } });
      bumpAvatarVersion();
      refreshUser();
    } catch (err: any) {
      setAvatarError(
        err?.response?.data?.error || err?.message || 'Failed to remove photo.',
      );
    }
  };

  const saveName = async () => {
    const trimmed = name.trim();
    if (!trimmed || trimmed === user?.name) return;
    setSaving(true);
    setNameError(null);
    try {
      await axios.put(
        '/api/user/profile',
        { name: trimmed },
        { headers: { Authorization: `Bearer ${token}` } },
      );
      refreshUser();
    } catch (err: any) {
      setNameError(
        err?.response?.data?.error || err?.message || 'Failed to save name.',
      );
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-[#2F2F2F] rounded-2xl shadow-xl w-full max-w-3xl h-[600px] max-h-[85vh] flex overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Section nav */}
        <div className="w-48 flex-shrink-0 bg-[#F7F7F8] dark:bg-[#242424] border-r border-gray-200 dark:border-gray-700 p-3">
          <h2 className="text-sm font-semibold px-2 mb-3 text-gray-900 dark:text-white">
            Settings
          </h2>
          <nav className="space-y-0.5">
            {NAV_ITEMS.map((item) => (
              <button
                key={item.id}
                onClick={() => setSection(item.id)}
                className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                  section === item.id
                    ? 'bg-gray-200 dark:bg-[#3F3F3F] text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-[#3F3F3F]'
                }`}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
            <h3 className="text-base font-semibold text-gray-900 dark:text-white">
              {NAV_ITEMS.find((i) => i.id === section)?.label}
            </h3>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-[#3F3F3F] transition-colors"
              aria-label="Close"
            >
              ✕
            </button>
          </div>

          <div className="flex-1 overflow-y-auto px-6 py-5">
            {section === 'general' && (
              <div className="space-y-8">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                    Profile picture
                  </h4>
                  <div className="flex items-center gap-4">
                    <UserAvatar
                      name={user?.name}
                      email={user?.email}
                      token={token}
                      hasAvatar={user?.hasAvatar}
                      avatarVersion={avatarVersion}
                      size="lg"
                    />
                    <div className="flex items-center gap-2">
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/png,image/jpeg,image/webp"
                        className="hidden"
                        onChange={(e) => {
                          const file = e.target.files?.[0];
                          if (file) uploadAvatar(file);
                          e.target.value = '';
                        }}
                      />
                      <button
                        onClick={() => fileInputRef.current?.click()}
                        className="px-3 py-1.5 rounded-lg text-sm bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
                      >
                        Upload photo
                      </button>
                      {user?.hasAvatar && (
                        <button
                          onClick={removeAvatar}
                          className="px-3 py-1.5 rounded-lg text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-[#3F3F3F] transition-colors"
                        >
                          Remove
                        </button>
                      )}
                    </div>
                  </div>
                  {avatarError && (
                    <p className="text-xs text-red-500 mt-2">{avatarError}</p>
                  )}
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                    Name
                  </h4>
                  <div className="flex items-center gap-2 max-w-sm">
                    <input
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') saveName();
                      }}
                      className="flex-1 bg-[#F7F7F8] dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-white focus:outline-none"
                      placeholder="Your name"
                    />
                    <button
                      onClick={saveName}
                      disabled={saving || !name.trim() || name.trim() === user?.name}
                      className="px-3 py-2 rounded-lg text-sm bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    >
                      Save
                    </button>
                  </div>
                  {nameError && <p className="text-xs text-red-500 mt-2">{nameError}</p>}
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">
                    Appearance
                  </h4>
                  <div className="flex gap-2">
                    {(['light', 'dark', 'system'] as ThemeMode[]).map((mode) => (
                      <button
                        key={mode}
                        onClick={() => setThemeMode(mode)}
                        className={`px-4 py-2 rounded-lg text-sm capitalize border transition-colors ${
                          themeMode === mode
                            ? 'border-gray-900 dark:border-white bg-gray-900 dark:bg-white text-white dark:text-gray-900'
                            : 'border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-[#3F3F3F]'
                        }`}
                      >
                        {mode}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {section === 'account' && (
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                    Email
                  </h4>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {user?.email || '—'}
                  </p>
                </div>
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  More account settings coming soon.
                </p>
              </div>
            )}

            {section === 'display' && (
              <p className="text-xs text-gray-400 dark:text-gray-500">
                More display settings coming soon.
              </p>
            )}

            {section === 'apiUsage' && (
              <div className="space-y-8">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                    Default model
                  </h4>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mb-3">
                    Used for new messages across all chats.
                  </p>
                  <select
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="w-full max-w-xs bg-[#F7F7F8] dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-white focus:outline-none"
                  >
                    {MODELS.map((m) => (
                      <option key={m} value={m}>
                        {m}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                    API keys
                  </h4>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mb-3">
                    Bring your own provider keys — used for your chats instead of the shared
                    default. Ollama runs locally and doesn't need a key.
                  </p>
                  {providerKeysLoading ? (
                    <p className="text-xs text-gray-400 dark:text-gray-500">Loading…</p>
                  ) : (
                    <div className="space-y-2 max-w-sm">
                      {PROVIDERS.map((p) => {
                        const isSet = !!providerKeys[p.id];
                        const isOpen = !!openProviders[p.id];
                        return (
                          <div key={p.id}>
                            <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-[#F7F7F8] dark:bg-[#1a1a1a]">
                              <span className="text-sm text-gray-700 dark:text-gray-300">
                                {p.label}
                              </span>
                              <div className="flex items-center gap-2">
                                <span
                                  className={`text-xs ${
                                    isSet
                                      ? 'text-green-600 dark:text-green-400'
                                      : 'text-gray-400 dark:text-gray-500'
                                  }`}
                                >
                                  {isSet ? 'API set' : 'Not set'}
                                </span>
                                <button
                                  onClick={() =>
                                    setOpenProviders((open) => ({ ...open, [p.id]: !isOpen }))
                                  }
                                  className="text-xs text-gray-600 dark:text-gray-300 hover:underline"
                                >
                                  {isOpen ? 'Cancel' : isSet ? 'Edit' : 'Set'}
                                </button>
                              </div>
                            </div>
                            {isOpen && (
                              <div className="mt-2">
                                <div className="flex items-center gap-2">
                                  <input
                                    type="password"
                                    autoFocus
                                    value={keyInputs[p.id] || ''}
                                    onChange={(e) =>
                                      setKeyInputs((inputs) => ({ ...inputs, [p.id]: e.target.value }))
                                    }
                                    onKeyDown={(e) => {
                                      if (e.key === 'Enter') saveProviderKey(p.id);
                                    }}
                                    placeholder={isSet ? 'Replace key…' : 'Enter API key…'}
                                    className="flex-1 bg-[#F7F7F8] dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-600 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-white focus:outline-none"
                                  />
                                  <button
                                    onClick={() => saveProviderKey(p.id)}
                                    disabled={keySaving[p.id] || !keyInputs[p.id]?.trim()}
                                    className="px-3 py-2 rounded-lg text-sm bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                                  >
                                    Save
                                  </button>
                                  {isSet && (
                                    <button
                                      onClick={() => removeProviderKey(p.id)}
                                      className="px-2 py-2 text-xs text-red-500 hover:text-red-600"
                                    >
                                      Remove
                                    </button>
                                  )}
                                </div>
                                {keyErrors[p.id] && (
                                  <p className="text-xs text-red-500 mt-1">{keyErrors[p.id]}</p>
                                )}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            )}

            {section === 'billing' && (
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                    Subscription
                  </h4>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mb-3">
                    Manage your plan and payment method via Stripe.
                  </p>
                  <button
                    onClick={openBillingPortal}
                    disabled={billingLoading}
                    className="px-3 py-1.5 rounded-lg text-sm bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                  >
                    {billingLoading ? 'Opening…' : 'Manage billing'}
                  </button>
                  {billingError && <p className="text-xs text-red-500 mt-2">{billingError}</p>}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
