import axios from 'axios';
import { useEffect, useState } from 'react';
import { API_BASE_URL } from '../constants/constants';

interface Props {
  name?: string;
  email?: string;
  token: string | null;
  hasAvatar?: boolean;
  avatarVersion?: number;
  size?: 'sm' | 'lg';
}

const SIZE_CLASSES: Record<'sm' | 'lg', string> = {
  sm: 'w-7 h-7 text-xs',
  lg: 'w-16 h-16 text-xl',
};

export default function UserAvatar({
  name,
  email,
  token,
  hasAvatar,
  avatarVersion,
  size = 'sm',
}: Props) {
  const [url, setUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!hasAvatar) {
      setUrl(null);
      return;
    }
    let objectUrl: string | null = null;
    let cancelled = false;

    (async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/user/avatar`, {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob',
        });
        if (cancelled) return;
        objectUrl = URL.createObjectURL(res.data as Blob);
        setUrl(objectUrl);
      } catch {
        if (!cancelled) setUrl(null);
      }
    })();

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [hasAvatar, token, avatarVersion]);

  const seed = name || email || '?';
  const letter = seed.trim().charAt(0).toUpperCase() || '?';

  return (
    <div
      className={`${SIZE_CLASSES[size]} rounded-full flex-shrink-0 flex items-center justify-center overflow-hidden font-semibold text-gray-900 dark:text-white bg-gray-200 dark:bg-gray-700`}
    >
      {url ? <img src={url} alt="" className="w-full h-full object-cover" /> : letter}
    </div>
  );
}
