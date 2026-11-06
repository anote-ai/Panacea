import { useState } from 'react';
import { useAuth } from '../App';
import { coworkerApi, errorMessage } from './api';
import { useCoworker } from './CoworkerContext';
import { Card, ghostBtn, inputCls, primaryBtn } from './ui';

const TOKEN_TOOLS = [
  {
    provider: 'github', label: 'GitHub', icon: '🐙', oauth: 'github_oauth' as const,
    what: 'Reads your PRs and reviews to learn how you work; opens PRs and posts reviews only when you approve.',
    hint: 'a personal access token (ghp_… or github_pat_…)', placeholder: 'ghp_…',
    valid: (t: string) => /^(ghp_|github_pat_|gho_)/.test(t) && t.length >= 20,
  },
  {
    provider: 'notion', label: 'Notion', icon: '📝', oauth: 'notion_oauth' as const,
    what: 'Reads the pages you share with it for specs and conventions; writes pages when you approve.',
    hint: 'an internal integration secret (ntn_…)', placeholder: 'ntn_…',
    valid: (t: string) => /^(ntn_|secret_)/.test(t) && t.length >= 20,
  },
] as const;

/** GitHub, Jira, Notion and MCP servers: what the AI engineer reads from and acts through. */
export default function DevToolsPanel({ returnTo = '/app/coworker/settings' }: { returnTo?: string }) {
  const { token } = useAuth();
  const { connections, capabilities, refresh } = useCoworker();
  const api = coworkerApi(token);
  const [tokens, setTokens] = useState<Record<string, string>>({});
  const [jira, setJira] = useState({ site: '', email: '', token: '' });
  const [server, setServer] = useState({ name: '', url: '', auth: '' });
  const [msg, setMsg] = useState('');
  const [busy, setBusy] = useState(false);
  const conn = (p: string) => connections.find((c) => c.provider === p);
  const mcpServers = connections.filter((c) => c.provider.startsWith('mcp_'));

  const run = async (fn: () => Promise<any>, done: string) => {
    setBusy(true);
    setMsg('');
    try {
      await fn();
      await refresh();
      setMsg(done);
    } catch (e) {
      setMsg(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };
  const oauth = async (provider: string) => {
    try {
      localStorage.setItem('coworker_return_to', returnTo);
      window.location.href = (await api.post(`/connections/${provider}/start`)).url;
    } catch (e) {
      setMsg(errorMessage(e));
    }
  };
  const disconnect = (provider: string, label: string) =>
    run(() => api.del(`/connections/${provider}`), `Disconnected ${label} and deleted what was synced from it.`);

  return (
    <div className="space-y-3">
      {TOKEN_TOOLS.map((t) => {
        const row = conn(t.provider);
        const value = tokens[t.provider] || '';
        const canOauth = Boolean(capabilities?.[t.oauth]);
        return (
          <Card key={t.provider} className="p-4">
            <div className="flex items-center gap-3">
              <span className="text-xl" aria-hidden>{t.icon}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium">{t.label}</p>
                <p className="text-xs text-gray-500">{row ? `${row.account} · ${row.status}. ${t.what}` : t.what}</p>
                {row?.error && <p className="text-xs text-red-500 mt-1">{row.error}</p>}
              </div>
              {row ? (
                <button className={ghostBtn} onClick={() => disconnect(t.provider, t.label)}>Disconnect</button>
              ) : canOauth ? (
                <button className={primaryBtn} onClick={() => oauth(t.provider)}>Connect</button>
              ) : null}
            </div>
            {!row && (
              <div className="flex gap-2 mt-3">
                <input className={inputCls} placeholder={t.placeholder} value={value} aria-label={`${t.label} token (${t.hint})`}
                  onChange={(e) => setTokens((x) => ({ ...x, [t.provider]: e.target.value }))} />
                <button className={ghostBtn} disabled={busy || !t.valid(value)}
                  onClick={() => run(() => api.post(`/connections/${t.provider}/token`, { token: value }), `Connected ${t.label}.`)}>
                  Use token
                </button>
              </div>
            )}
          </Card>
        );
      })}

      <Card className="p-4">
        <div className="flex items-center gap-3">
          <span className="text-xl" aria-hidden>🎫</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium">Jira</p>
            <p className="text-xs text-gray-500">
              {conn('jira') ? `${conn('jira')!.account} · ${conn('jira')!.status}. ` : ''}
              Tickets become specs for the AI engineer. Comments and new issues wait for your approval.
            </p>
            {conn('jira')?.error && <p className="text-xs text-red-500 mt-1">{conn('jira')!.error}</p>}
          </div>
          {conn('jira') && <button className={ghostBtn} onClick={() => disconnect('jira', 'Jira')}>Disconnect</button>}
        </div>
        {!conn('jira') && (
          <div className="grid sm:grid-cols-3 gap-2 mt-3">
            <input className={inputCls} placeholder="acme.atlassian.net" value={jira.site} aria-label="Jira site"
              onChange={(e) => setJira({ ...jira, site: e.target.value })} />
            <input className={inputCls} placeholder="you@acme.com" value={jira.email} aria-label="Atlassian email"
              onChange={(e) => setJira({ ...jira, email: e.target.value })} />
            <div className="flex gap-2">
              <input className={inputCls} type="password" placeholder="API token" value={jira.token} aria-label="Jira API token"
                onChange={(e) => setJira({ ...jira, token: e.target.value })} />
              <button className={ghostBtn} disabled={busy || !jira.site || !jira.email.includes('@') || jira.token.length < 16}
                onClick={() => run(() => api.post('/connections/jira/token', jira), 'Connected Jira.')}>
                Connect
              </button>
            </div>
          </div>
        )}
      </Card>

      <Card className="p-4">
        <div className="flex items-center gap-3">
          <span className="text-xl" aria-hidden>🧩</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium">MCP servers</p>
            <p className="text-xs text-gray-500">
              Plug in any Model Context Protocol server (Linear, Sentry, your own tools). Every tool call waits for your approval
              unless you change its autonomy.
            </p>
          </div>
        </div>
        {mcpServers.map((m) => (
          <div key={m.provider} className="flex items-center gap-3 mt-3 text-sm">
            <span className="flex-1 min-w-0 truncate">
              <span className="font-medium">{m.name || m.provider.slice(4)}</span>
              <span className="text-gray-500"> · {(m.tools || []).length} tools{m.tools?.length ? `: ${m.tools.slice(0, 4).join(', ')}` : ''}</span>
            </span>
            <button className={ghostBtn} onClick={() => disconnect(m.provider, m.name || 'the server')}>Remove</button>
          </div>
        ))}
        <div className="grid sm:grid-cols-3 gap-2 mt-3">
          <input className={inputCls} placeholder="Name (e.g. Linear)" value={server.name} aria-label="MCP server name"
            onChange={(e) => setServer({ ...server, name: e.target.value })} />
          <input className={inputCls} placeholder="https://mcp.example.com/mcp" value={server.url} aria-label="MCP server URL"
            onChange={(e) => setServer({ ...server, url: e.target.value })} />
          <div className="flex gap-2">
            <input className={inputCls} type="password" placeholder="Bearer token (optional)" value={server.auth}
              aria-label="MCP server token" onChange={(e) => setServer({ ...server, auth: e.target.value })} />
            <button className={ghostBtn} disabled={busy || !server.name || !server.url}
              onClick={() => run(async () => {
                await api.post('/connections/mcp', server);
                setServer({ name: '', url: '', auth: '' });
              }, `Connected ${server.name}.`)}>
              Add
            </button>
          </div>
        </div>
      </Card>
      {msg && <p className="text-sm text-gray-600 dark:text-gray-300">{msg}</p>}
    </div>
  );
}
