import axios from 'axios';
import { useEffect, useState } from 'react';
import { API_BASE_URL } from '../constants/constants';

interface Props {
  docId: string;
  token: string | null;
  size?: 'sm' | 'md' | 'lg';
}

const SIZE_CLASSES: Record<'sm' | 'md' | 'lg', string> = {
  sm: 'w-7 h-9 text-sm',
  md: 'w-9 h-12 text-lg',
  // 'lg' fills its parent — wrap it in a sized/aspect-ratio container.
  lg: 'w-full h-full text-4xl',
};

export default function DocThumbnail({ docId, token, size = 'md' }: Props) {
  const [url, setUrl] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let objectUrl: string | null = null;
    let cancelled = false;
    setUrl(null);
    setFailed(false);

    (async () => {
      try {
        const res = await axios.get(`${API_BASE_URL}/api/documents/${docId}/thumbnail`, {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob',
        });
        if (cancelled) return;
        objectUrl = URL.createObjectURL(res.data as Blob);
        setUrl(objectUrl);
      } catch {
        if (!cancelled) setFailed(true);
      }
    })();

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [docId, token]);

  return (
    <div
      className={`${SIZE_CLASSES[size]} rounded border border-gray-200 dark:border-gray-700 flex items-center justify-center overflow-hidden bg-white dark:bg-[#1a1a1a] flex-shrink-0`}
    >
      {url && !failed ? (
        <img src={url} alt="" className="w-full h-full object-cover" />
      ) : (
        <span>📄</span>
      )}
    </div>
  );
}
