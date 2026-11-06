import { useEffect, useState } from 'react';
import { useAuth } from '../../App';
import { coworkerApi, errorMessage, timeAgo } from '../api';
import { Card, Empty, Pill, Section, ghostBtn, inputCls, primaryBtn } from '../ui';

function Evidence({ items }: { items: any[] }) {
  if (!items?.length) return null;
  return (
    <p className="text-[11px] text-gray-500 mt-1 truncate">
      From:{' '}
      {items.map((e, i) => (
        <span key={i}>
          {i > 0 && ' · '}
          {e.url ? <a className="underline" href={e.url} target="_blank" rel="noreferrer">{e.title || e.source}</a> : e.title}
        </span>
      ))}
    </p>
  );
}

/** "Create your own AI": what it learned about how you work, from your code, reviews, tickets and docs. */
export default function KnowledgeTab() {
  const { token } = useAuth();
  const api = coworkerApi(token);
  const [pack, setPack] = useState<any>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [newRule, setNewRule] = useState('');
  const [editing, setEditing] = useState<{ id: string; text: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');

  const load = async () => {
    const [p, v] = await Promise.all([api.get('/knowledge-pack'), api.get('/knowledge-pack/versions')]);
    setPack(p);
    setVersions(v.versions);
  };
  useEffect(() => {
    load().catch((e) => setMsg(errorMessage(e)));
  }, []);
  const act = async (fn: () => Promise<any>, done = '') => {
    setBusy(true);
    setMsg('');
    try {
      const out = await fn();
      if (out?.styleRules) setPack(out);
      setVersions((await api.get('/knowledge-pack/versions')).versions);
      setMsg(done);
    } catch (e) {
      setMsg(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };
  const edit = (section: string, op: string, id = '', values: Record<string, any> = {}) =>
    act(() => api.patch('/knowledge-pack', { section, op, id, values }));

  if (!pack) return <div className="h-40 animate-pulse" />;
  const stats = pack.stats || {};
  const empty = !pack.skills.length && !pack.styleRules.length && !pack.playbooks.length;

  return (
    <div>
      <Section title="Your knowledge pack"
        subtitle="How you work, learned from your own pull requests, reviews, tickets and docs. Your AI engineer and code reviewer follow it. Edit anything; your edits survive every rebuild."
        action={
          <div className="flex gap-2">
            <button className={ghostBtn} disabled={busy} onClick={() => act(() => api.post('/knowledge-pack/build'), 'Rebuilt from your latest work.')}>Rebuild</button>
            <button className={primaryBtn} disabled={busy || empty}
              onClick={() => act(() => api.post('/knowledge-pack/versions'), 'Saved a new version.')}>Save version</button>
          </div>
        }>
        <p className="text-xs text-gray-500">
          Learned from {stats.pull_requests || 0} pull requests, {stats.review_comments || 0} review comments, {stats.tickets || 0} tickets
          and {stats.pages || 0} docs{pack.sources?.length ? ` (${pack.sources.join(', ')})` : ''}. Secrets and other people's contact
          details are removed. Updated {timeAgo(pack.updatedAt)}.
        </p>
        {empty && <div className="mt-3"><Empty title="Nothing to learn from yet">Connect GitHub, Jira or Notion in Settings, then rebuild.</Empty></div>}
      </Section>

      {pack.skills.length > 0 && (
        <Section title="Skills">
          <div className="flex flex-wrap gap-2">
            {pack.skills.map((s: any) => (
              <span key={s.id} className="inline-flex items-center gap-1.5 rounded-full border border-gray-200 dark:border-gray-700 px-3 py-1 text-sm"
                title={(s.evidence || []).map((e: any) => e.title).join('\n')}>
                {s.name} <span className="text-xs text-gray-500">{s.weight}</span>
                <button aria-label={`Remove ${s.name}`} className="text-gray-400 hover:text-red-500" onClick={() => edit('skills', 'remove', s.id)}>✕</button>
              </span>
            ))}
          </div>
        </Section>
      )}

      <Section title="Style rules" subtitle="The standards you hold code to. Rules with a check are enforced by the code reviewer.">
        <div className="space-y-2">
          {pack.styleRules.map((r: any) => (
            <Card key={r.id} className="p-3">
              {editing?.id === r.id ? (
                <div className="flex gap-2">
                  <input className={inputCls} value={editing!.text} onChange={(e) => setEditing({ id: r.id, text: e.target.value })} />
                  <button className={primaryBtn} onClick={() => { edit('style_rules', 'update', r.id, { text: editing!.text }); setEditing(null); }}>Save</button>
                </div>
              ) : (
                <div className="flex items-start gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm">{r.text}</p>
                    {r.quotes?.[0] && <p className="text-xs text-gray-500 italic mt-0.5">“{r.quotes[0]}”</p>}
                    <Evidence items={r.evidence} />
                  </div>
                  {r.check && <Pill tone="blue">checked</Pill>}
                  {r.edited && <Pill>edited</Pill>}
                  <button className="text-xs underline text-gray-500" onClick={() => setEditing({ id: r.id, text: r.text })}>Edit</button>
                  <button className="text-xs underline text-gray-500" onClick={() => edit('style_rules', 'remove', r.id)}>Remove</button>
                </div>
              )}
            </Card>
          ))}
          <div className="flex gap-2">
            <input className={inputCls} placeholder="Add a rule, e.g. “Never use floats for money”" value={newRule}
              onChange={(e) => setNewRule(e.target.value)} />
            <button className={ghostBtn} disabled={!newRule.trim()} onClick={() => { edit('style_rules', 'add', '', { text: newRule }); setNewRule(''); }}>Add</button>
          </div>
        </div>
      </Section>

      <Section title="Playbooks" subtitle="How you do recurring work.">
        <div className="grid sm:grid-cols-2 gap-3">
          {pack.playbooks.map((pb: any) => (
            <Card key={pb.id} className="p-3">
              <div className="flex items-center gap-2">
                <p className="text-sm font-medium flex-1">{pb.title}</p>
                <button className="text-xs underline text-gray-500" onClick={() => edit('playbooks', 'remove', pb.id)}>Remove</button>
              </div>
              <ol className="list-decimal pl-5 text-sm mt-1 space-y-0.5">{pb.steps.map((s: string, i: number) => <li key={i}>{s}</li>)}</ol>
              <Evidence items={pb.evidence} />
            </Card>
          ))}
        </div>
      </Section>

      {versions.length > 0 && (
        <Section title="Saved versions" subtitle="A saved version is fixed. It's what a marketplace listing will point to.">
          <ul className="text-sm space-y-1">
            {versions.map((v) => <li key={v.version}>Version {v.version} · {timeAgo(v.createdAt)} · {(v.sources || []).join(', ')}</li>)}
          </ul>
        </Section>
      )}
      {msg && <p className="text-sm text-gray-600 dark:text-gray-300">{msg}</p>}
    </div>
  );
}
