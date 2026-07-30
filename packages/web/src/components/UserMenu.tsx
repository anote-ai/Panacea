import { useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../App';
import SettingsModal from './SettingsModal';
import UserAvatar from './UserAvatar';

interface Props {
  sidebarOpen: boolean;
}

export default function UserMenu({ sidebarOpen }: Props) {
  const { token, setToken, user, avatarVersion } = useAuth();
  const nav = useNavigate();
  const [open, setOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [pos, setPos] = useState<{ left: number; bottom: number } | null>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  const openMenu = () => {
    const rect = triggerRef.current?.getBoundingClientRect();
    if (rect) {
      setPos({ left: rect.left, bottom: window.innerHeight - rect.top + 8 });
    }
    setOpen(true);
  };

  const logout = () => {
    setToken(null);
    nav('/login');
  };

  const displayName = user?.name || user?.email || 'Account';

  return (
    <div className="p-3 border-t border-gray-200 dark:border-gray-700">
      <button
        ref={triggerRef}
        onClick={openMenu}
        title={displayName}
        className={`w-full rounded-lg text-sm hover:bg-gray-200 dark:hover:bg-[#2F2F2F] transition-colors flex items-center gap-2 ${
          sidebarOpen ? 'text-left px-2 py-2' : 'justify-center py-2'
        }`}
      >
        <UserAvatar
          name={user?.name}
          email={user?.email}
          token={token}
          hasAvatar={user?.hasAvatar}
          avatarVersion={avatarVersion}
          size="sm"
        />
        {sidebarOpen && (
          <span className="truncate text-gray-700 dark:text-gray-300">
            {displayName}
          </span>
        )}
      </button>

      {open &&
        pos &&
        createPortal(
          <>
            <div
              className="fixed inset-0 z-40"
              onClick={() => setOpen(false)}
            />
            <div
              className="fixed z-50 w-64 bg-white dark:bg-[#2F2F2F] rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 p-3"
              style={{ left: pos.left, bottom: pos.bottom }}
            >
              <div className="flex items-center gap-3 mb-3 px-1">
                <UserAvatar
                  name={user?.name}
                  email={user?.email}
                  token={token}
                  hasAvatar={user?.hasAvatar}
                  avatarVersion={avatarVersion}
                  size="lg"
                />
                <div className="min-w-0">
                  <p className="text-sm font-medium truncate text-gray-900 dark:text-white">
                    {displayName}
                  </p>
                  {user?.email && (
                    <p className="text-xs text-gray-400 dark:text-gray-500 truncate">
                      {user.email}
                    </p>
                  )}
                </div>
              </div>
              <button
                onClick={() => {
                  setOpen(false);
                  setSettingsOpen(true);
                }}
                className="w-full text-left px-3 py-2 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-[#3F3F3F] transition-colors"
              >
                Settings
              </button>
              <div className="my-1 border-t border-gray-200 dark:border-gray-700" />
              <button
                onClick={logout}
                className="w-full text-left px-3 py-2 rounded-lg text-sm text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-[#3F3F3F] transition-colors flex items-center gap-2"
              >
                <span></span> Sign Out
              </button>
            </div>
          </>,
          document.body,
        )}

      <SettingsModal
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />
    </div>
  );
}
