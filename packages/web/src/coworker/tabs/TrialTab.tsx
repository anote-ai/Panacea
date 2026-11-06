import { useEffect, useState } from 'react';
import { useAuth } from '../../App';
import { coworkerApi, errorMessage, timeAgo } from '../api';
import { Card, Empty, Pill, Section, ghostBtn, inputCls, primaryBtn } from '../ui';

const ROLES: Record<string, string> = {
  engineering: 'Software engineer', sales: 'SDR', marketing: 'Marketer', healthcare: 'Front-office admin',
  operations: 'Operations admin', assistant: 'Executive assistant',
};

function fmt(metric: string, metrics: Record<string, any>, v: number | null) {
  if (v === null || v === undefined) return '—';
  return metrics[metric]?.kind === 'ratio' ? `${Math.round(v * 100)}%` : String(Math.round(v * 10) / 10);
}

function Goals({ goals, metrics }: { goals: any[]; metrics: Record<string, any> }) {
  return (
    <Card className="divide-y divide-gray-100 dark:divide-gray-700">
      {goals.map((g) => (
        <div key={g.metric} className="flex items-center gap-3 px-4 py-2.5 text-sm">
          <span className="flex-1">{g.label}</span>
          <span className="tabular-nums">{fmt(g.metric, metrics, g.actual)} / {fmt(g.metric, metrics, g.target)}</span>
          <Pill tone={g.met ? 'green' : g.onTrack ? 'blue' : 'amber'}>{g.met ? 'Met' : g.onTrack ? 'On track' : 'Behind'}</Pill>
        </div>
      ))}
    </Card>
  );
}

function OperatorView() {
  const { token } = useAuth();
  const api = coworkerApi(token);
  const [trials, setTrials] = useState<any[] | null>(null);
  const [notes, setNotes] = useState<Record<number, string>>({});
  const [msg, setMsg] = useState('');
  useEffect(() => {
    api.get('/operator/trials').then((d) => setTrials(d.trials)).catch(() => setTrials(null));
  }, []);
  if (!trials) return null;
  const send = async (id: number) => {
    try {
      await api.post(`/operator/trials/${id}/notes`, { text: notes[id] || '' });
      setNotes((n) => ({ ...n, [id]: '' }));
      setMsg('Note sent.');
    } catch (e) {
      setMsg(errorMessage(e));
    }
  };
  return (
    <Section title="Operator view" subtitle="Every running trial. You can leave a note; approvals stay with the customer.">
      {trials.length === 0 ? <Empty title="No trials running" /> : (
        <div className="space-y-3">
          {trials.map((t) => (
            <Card key={t.id} className="p-4">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm font-medium flex-1">{t.owner} · {t.roleLabel}</span>
                <Pill>Day {t.progress.day} of {t.progress.of}</Pill>
                <Pill tone={t.progress.met === t.progress.goals.length ? 'green' : 'gray'}>{t.progress.met}/{t.progress.goals.length} goals</Pill>
                {t.flags.waiting > 0 && <Pill tone="amber">{t.flags.waiting} flagged</Pill>}
                {t.flags.failed > 0 && <Pill tone="red">{t.flags.failed} failed</Pill>}
                {t.flags.escalatedReviews > 0 && <Pill tone="amber">{t.flags.escalatedReviews} escalated reviews</Pill>}
              </div>
              <div className="flex gap-2 mt-3">
                <input className={inputCls} placeholder="Note to the customer" value={notes[t.id] || ''}
                  onChange={(e) => setNotes((n) => ({ ...n, [t.id]: e.target.value }))} />
                <button className={ghostBtn} disabled={!notes[t.id]?.trim()} onClick={() => send(t.id)}>Send</button>
              </div>
            </Card>
          ))}
        </div>
      )}
      {msg && <p className="text-sm text-gray-500 mt-2">{msg}</p>}
    </Section>
  );
}

/** The one-month trial: goals agreed in week one, weekly reports, then convert, extend, or cancel. */
export default function TrialTab() {
  const { token } = useAuth();
  const api = coworkerApi(token);
  const [data, setData] = useState<any>(null);
  const [role, setRole] = useState('engineering');
  const [goals, setGoals] = useState<any[]>([]);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');

  const load = async () => {
    const d = await api.get('/trial');
    setData(d);
    setGoals(d.trial ? d.trial.goals : d.defaults[role]);
  };
  useEffect(() => {
    load().catch((e) => setMsg(errorMessage(e)));
  }, []);
  useEffect(() => {
    if (data && !data.trial) setGoals(data.defaults[role]);
  }, [role]);

  const act = async (fn: () => Promise<any>, done = '') => {
    setBusy(true);
    setMsg('');
    try {
      const out = await fn();
      if (out?.billing?.url) window.location.href = out.billing.url;
      await load();
      setMsg(out?.billing?.error || done);
    } catch (e) {
      setMsg(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  if (!data) return <div className="h-40 animate-pulse" />;
  const t = data.trial;
  const metrics = data.metrics;
  const editor = (
    <div className="space-y-2">
      {goals.map((g, i) => (
        <div key={i} className="flex gap-2">
          <select className={inputCls} value={g.metric} onChange={(e) => setGoals(goals.map((x, j) => (j === i ? { ...x, metric: e.target.value } : x)))}>
            {Object.entries(metrics).map(([k, m]: any) => <option key={k} value={k}>{m.label}</option>)}
          </select>
          <input className={`${inputCls} max-w-[8rem]`} type="number" step="any" value={g.target} aria-label="Target"
            onChange={(e) => setGoals(goals.map((x, j) => (j === i ? { ...x, target: e.target.value } : x)))} />
          <button className={ghostBtn} aria-label="Remove goal" onClick={() => setGoals(goals.filter((_, j) => j !== i))}>✕</button>
        </div>
      ))}
      <button className="text-xs underline text-gray-500" onClick={() => setGoals([...goals, { metric: 'totalOutput', target: 10 }])}>+ Add a goal</button>
      <p className="text-xs text-gray-500">Ratios are 0–1 (0.8 = 80%).</p>
    </div>
  );

  return (
    <div>
      {!t || t.status === 'cancelled' || t.status === 'converted' ? (
        <Section title="Start a one-month trial"
          subtitle="Pick the seat it fills and agree on what success looks like. You get a report every week and decide after 30 days.">
          <Card className="p-4 space-y-3">
            <label className="text-sm block">Role
              <select className={`${inputCls} mt-1`} value={role} onChange={(e) => setRole(e.target.value)}>
                {Object.entries(ROLES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
              </select>
            </label>
            <p className="text-sm font-medium">Goals for day 30</p>
            {editor}
            <p className="text-xs text-gray-500">{data.guarantee}</p>
            <button className={primaryBtn} disabled={busy || goals.length === 0}
              onClick={() => act(() => api.post('/trial', { role, goals }), 'Trial started.')}>Start the trial</button>
          </Card>
        </Section>
      ) : (
        <>
          <Section title={`Trial: ${t.roleLabel}`}
            subtitle={`Day ${t.progress.day} of ${t.progress.of}. Started ${timeAgo(t.startedAt)}. Approver: ${t.approver}.`}>
            {!t.goalsLocked ? (
              <Card className="p-4 space-y-3">
                <p className="text-sm">Agree on the goals this week. They lock after day 7, so the trial is judged on what you agreed.</p>
                {editor}
                <button className={ghostBtn} disabled={busy} onClick={() => act(() => api.put('/trial/goals', { goals }), 'Goals saved.')}>Save goals</button>
              </Card>
            ) : null}
            <div className="mt-3"><Goals goals={t.progress.goals} metrics={metrics} /></div>
            <p className="text-xs text-gray-500 mt-2">
              Cost so far ${t.progress.scorecard.cost.totalUsd.toFixed(2)} vs about ${Math.round(t.progress.scorecard.vsHire.hireCostUsd).toLocaleString()} for a{' '}
              {t.progress.scorecard.vsHire.roleLabel.toLowerCase()} (benchmark).
            </p>
          </Section>

          {t.status === 'ended' && (
            <Section title="Decide" subtitle={`${t.outcome.met} of ${t.outcome.of} goals met. ${t.guarantee}`}>
              <div className="flex gap-2 flex-wrap">
                <button className={primaryBtn} disabled={busy} onClick={() => act(() => api.post('/trial/decide', { choice: 'convert', plan: 'coworker' }))}>Keep it (paid plan)</button>
                {!t.outcome.extended && <button className={ghostBtn} disabled={busy} onClick={() => act(() => api.post('/trial/decide', { choice: 'extend' }), 'Extended by 14 days.')}>Extend 14 days</button>}
                <button className={ghostBtn} disabled={busy} onClick={() => act(() => api.post('/trial/decide', { choice: 'cancel' }), 'Trial ended.')}>End it</button>
              </div>
            </Section>
          )}

          {t.reports.length > 0 && (
            <Section title="Reports">
              <ul className="text-sm space-y-1">
                {t.reports.slice().reverse().map((r: any) => (
                  <li key={r.key}>{r.final ? 'Final report' : `Week ${r.week}`} · {timeAgo(r.at)} · {r.met}/{r.goals.length} goals met</li>
                ))}
              </ul>
            </Section>
          )}
        </>
      )}
      {msg && <p className="text-sm text-gray-600 dark:text-gray-300">{msg}</p>}
      <OperatorView />
    </div>
  );
}
