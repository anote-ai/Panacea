import { useEffect, useState } from 'react';
import { useAuth } from '../App';
import { coworkerApi, errorMessage, timeAgo } from './api';
import { Card, ghostBtn, inputCls } from './ui';

/** Personal access tokens for the SDK and CLI. A token can hand off work and read results; it can't approve anything. */
export default function ApiTokensCard() {
  const { token } = useAuth();
  const api = coworkerApi(token);
  const [tokens, setTokens] = useState<any[]>([]);
  const [name, setName] = useState('');
  const [fresh, setFresh] = useState('');
  const [msg, setMsg] = useState('');
  const load = () => api.get('/tokens').then((d) => setTokens(d.tokens)).catch((e) => setMsg(errorMessage(e)));
  useEffect(() => {
    load();
  }, []);

  const create = async () => {
    try {
      const d = await api.post('/tokens', { name });
      setFresh(d.token);
      setName('');
      load();
    } catch (e) {
      setMsg(errorMessage(e));
    }
  };
  const revoke = async (id: number) => {
    try {
      await api.del(`/tokens/${id}`);
      load();
    } catch (e) {
      setMsg(errorMessage(e));
    }
  };

  return (
    <Card className="p-4 space-y-3">
      <p className="text-sm text-gray-600 dark:text-gray-300">
        For the SDK, the CLI (<code className="text-xs">anote coworker login --token …</code>) and scripts. A token can hand work
        to the AI engineer, request reviews, and read results. Approving, sending and billing always happen here.
      </p>
      {fresh && (
        <div className="rounded-lg border border-amber-300 bg-amber-50 dark:bg-amber-500/10 p-3 text-sm">
          <p className="font-medium">Copy it now: it won't be shown again.</p>
          <div className="flex gap-2 mt-2">
            <code className="flex-1 break-all text-xs bg-white dark:bg-black/30 rounded px-2 py-1.5">{fresh}</code>
            <button className={ghostBtn} onClick={() => navigator.clipboard?.writeText(fresh)}>Copy</button>
          </div>
        </div>
      )}
      {tokens.map((t) => (
        <div key={t.id} className="flex items-center gap-3 text-sm">
          <span className="flex-1"><span className="font-medium">{t.name}</span> <code className="text-xs text-gray-500">{t.prefix}…</code></span>
          <span className="text-xs text-gray-500">{t.lastUsedAt ? `used ${timeAgo(t.lastUsedAt)}` : 'never used'}</span>
          <button className={ghostBtn} onClick={() => revoke(t.id)}>Revoke</button>
        </div>
      ))}
      <div className="flex gap-2">
        <input className={inputCls} placeholder="Name, e.g. CI or laptop" value={name} onChange={(e) => setName(e.target.value)} />
        <button className={ghostBtn} onClick={create}>Create token</button>
      </div>
      {msg && <p className="text-sm text-red-600">{msg}</p>}
    </Card>
  );
}
