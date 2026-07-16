import axios from 'axios';
import { useEffect, useRef, useState } from 'react';
import { type ThemeMode, useAuth, useTheme } from '../App';
import UserAvatar from './UserAvatar';

interface Props {
  open: boolean;
  onClose: () => void;
}

type Section = 'general' | 'account' | 'display';

const NAV_ITEMS: { id: Section; label: string }[] = [
  { id: 'general', label: 'General' },
  { id: 'account', label: 'Account' },
  { id: 'display', label: 'Display' },
];

export default function SettingsModal({ open, onClose }: Props) {
  const { token, user, refreshUser, avatarVersion, bumpAvatarVersion } = useAuth();
  const { themeMode, setThemeMode } = useTheme();
  const [section, setSection] = useState<Section>('general');
  const [name, setName] = useState(user?.name || '');
  const [saving, setSaving] = useState(false);
  const [avatarError, setAvatarError] = useState<string | null>(null);
  const [nameError, setNameError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setSection('general');
      setName(user?.name || '');
      setAvatarError(null);
      setNameError(null);
    }
  }, [open, user?.name]);

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
          </div>
        </div>
      </div>
    </div>
  );
}
