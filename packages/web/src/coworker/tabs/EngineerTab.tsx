import { useEffect, useState } from 'react';
import { useAuth } from '../../App';
import ActionCard from '../ActionCard';
import { coworkerApi, errorMessage, timeAgo } from '../api';
import { useCoworker } from '../CoworkerContext';
import { Card, Empty, Pill, Section, ghostBtn, inputCls, primaryBtn } from '../ui';

type Tone = 'gray' | 'green' | 'amber' | 'red' | 'blue';
const STATUS: Record<string, { label: string; tone: Tone }> = {
  spec: { label: 'Confirm the spec', tone: 'amber' },
  planned: { label: 'Review the plan', tone: 'amber' },
  running: { label: 'Working', tone: 'blue' },
  ready: { label: 'PR waiting for you', tone: 'amber' },
  pr_opened: { label: 'PR opened', tone: 'green' },
  failed: { label: 'Failed', tone: 'red' },
  needs_model: { label: 'Needs a model', tone: 'gray' },
};
const SEVERITY_TONE: Record<string, Tone> = { high: 'red', medium: 'amber', low: 'gray' };

function List({ items, onChange }: { items: string[]; onChange?: (next: string[]) => void }) {
  if (!onChange) return <ul className="list-disc pl-5 text-sm space-y-0.5">{items.map((c, i) => <li key={i}>{c}</li>)}</ul>;
  return (
    <div className="space-y-1.5">
      {items.map((c, i) => (
        <div key={i} className="flex gap-2">
          <input className={inputCls} value={c} onChange={(e) => onChange(items.map((x, j) => (j === i ? e.target.value : x)))} />
          <button className={ghostBtn} aria-label="Remove" onClick={() => onChange(items.filter((_, j) => j !== i))}>✕</button>
        </div>
      ))}
      <button className="text-xs underline text-gray-500" onClick={() => onChange([...items, ''])}>+ Add</button>
    </div>
  );
}

function Findings({ review, onDismiss }: { review: any; onDismiss?: (id: string, scope: string) => void }) {
  if (!review) return null;
  return (
    <div className="space-y-2">
      <p className="text-sm">
        {review.summary} {review.slop?.score !== undefined && <span className="text-gray-500">· Slop score {review.slop.score}/100</span>}
      </p>
      {review.escalate && <p className="text-xs text-amber-700 dark:text-amber-300">Flagged for a human: {review.reasons.join('; ')}</p>}
      {review.findings.filter((f: any) => !f.dismissed).map((f: any) => (
        <div key={f.id} className="rounded-lg border border-gray-200 dark:border-gray-700 p-3 text-sm">
          <div className="flex items-center gap-2 flex-wrap">
            <Pill tone={SEVERITY_TONE[f.severity]}>{f.severity}</Pill>
            <span className="font-medium">{f.title}</span>
            {f.path && <span className="font-mono text-xs text-gray-500">{f.path}{f.line ? `:${f.line}` : ''}</span>}
            {f.rule && <Pill tone="blue">{f.rule}</Pill>}
          </div>
          <p className="text-gray-600 dark:text-gray-300 mt-1">{f.detail}</p>
          <p className="text-gray-500 mt-1">Suggestion: {f.suggestion}</p>
          {onDismiss && (
            <div className="flex gap-3 mt-2 text-xs">
              <button className="underline text-gray-500" onClick={() => onDismiss(f.id, 'once')}>Dismiss</button>
              <button className="underline text-gray-500" onClick={() => onDismiss(f.id, 'repo')}>Don't flag this in {review.repo}</button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

function RunView({ run, onChange }: { run: any; onChange: (run: any) => void }) {
  const { token } = useAuth();
  const api = coworkerApi(token);
  const [spec, setSpec] = useState(run.spec);
  const [review, setReview] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');
  useEffect(() => setSpec(run.spec), [run.id, run.status]);
  useEffect(() => {
    if (run.reviewId) api.get(`/reviews/${run.reviewId}`).then(setReview).catch(() => setReview(null));
  }, [run.reviewId]);

  const call = async (fn: () => Promise<any>) => {
    setBusy(true);
    setMsg('');
    try {
      onChange(await fn());
    } catch (e) {
      setMsg(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };
  const status = STATUS[run.status] || { label: run.status, tone: 'gray' as Tone };
  const editing = run.status === 'spec';

  return (
    <Card className="p-4 space-y-4">
      <div className="flex items-start gap-3">
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold">{run.title}</p>
          <p className="text-xs text-gray-500">
            {run.repo} · {spec.source?.ref || 'from chat'} · started {timeAgo(run.createdAt)}
            {run.costUsd > 0 && ` · $${run.costUsd.toFixed(2)}`}
          </p>
        </div>
        <Pill tone={status.tone}>{status.label}</Pill>
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-wide text-gray-500 mb-1">1 · Spec</p>
        {editing ? (
          <div className="space-y-2">
            <input className={inputCls} value={spec.goal} aria-label="Goal" onChange={(e) => setSpec({ ...spec, goal: e.target.value })} />
            <p className="text-xs text-gray-500">Acceptance criteria (each one testable)</p>
            <List items={spec.acceptance_criteria || []} onChange={(v) => setSpec({ ...spec, acceptance_criteria: v })} />
            <p className="text-xs text-gray-500">Constraints</p>
            <List items={spec.constraints || []} onChange={(v) => setSpec({ ...spec, constraints: v })} />
            <input className={inputCls} value={spec.repo} aria-label="Repository" placeholder="owner/repo"
              onChange={(e) => setSpec({ ...spec, repo: e.target.value })} />
            <button className={primaryBtn} disabled={busy} onClick={() => call(async () => {
              await api.patch(`/engineer/runs/${run.id}/spec`, spec);
              return api.post(`/engineer/runs/${run.id}/plan`);
            })}>
              Looks right, plan it
            </button>
          </div>
        ) : (
          <>
            <p className="text-sm">{spec.goal}</p>
            <List items={spec.acceptance_criteria || []} />
          </>
        )}
      </div>

      {run.graph?.length > 0 && (
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-500 mb-1">2 · Task graph</p>
          <div className="space-y-2">
            {run.layers.map((layer: string[], i: number) => (
              <div key={i} className="flex flex-wrap gap-2 items-stretch">
                <span className="text-xs text-gray-400 w-14 pt-2">Step {i + 1}</span>
                {layer.map((id) => {
                  const node = run.graph.find((n: any) => n.id === id);
                  const state = run.nodes?.[id]?.status || 'pending';
                  return (
                    <div key={id} className="flex-1 min-w-[10rem] rounded-lg border border-gray-200 dark:border-gray-700 px-3 py-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium flex-1">{node?.title}</span>
                        <Pill tone={state === 'done' ? 'green' : state === 'skipped' ? 'gray' : 'blue'}>{state}</Pill>
                      </div>
                      <p className="font-mono text-[11px] text-gray-500 mt-0.5">{(node?.files || []).join(', ')}</p>
                      {run.nodes?.[id]?.pack_refs?.length > 0 && (
                        <p className="text-[11px] text-gray-500 mt-0.5">Followed: {run.nodes[id].pack_refs.join(', ')}</p>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
          {run.status === 'planned' && (
            <div className="flex gap-2 mt-3">
              <button className={primaryBtn} disabled={busy} onClick={() => call(() => api.post(`/engineer/runs/${run.id}/start`))}>
                Start the work
              </button>
              <button className={ghostBtn} disabled={busy} onClick={() => call(() => api.patch(`/engineer/runs/${run.id}/spec`, {}))}>
                Edit the spec
              </button>
            </div>
          )}
        </div>
      )}

      {Object.keys(run.checks || {}).length > 0 && (
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-500 mb-1">3 · Checks</p>
          <p className="text-sm">
            {run.checks.passed ? '✅ Tests passed' : run.checks.passed === false ? '❌ Tests failed' : `⚪ ${run.checks.output}`}
            {run.checks.fix_attempts > 0 && ` after ${run.checks.fix_attempts} fix attempt(s)`}
          </p>
          {run.checks.ran && (
            <details className="text-xs mt-1">
              <summary className="cursor-pointer text-gray-500">Test output</summary>
              <pre className="mt-1 max-h-48 overflow-auto rounded bg-[#F7F7F8] dark:bg-[#2F2F2F] p-2 whitespace-pre-wrap">{run.checks.output}</pre>
            </details>
          )}
        </div>
      )}

      {review && (
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-500 mb-1">4 · AI review</p>
          <Findings review={review} />
        </div>
      )}

      {run.actionId && (
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-gray-500 mb-1">5 · Your approval</p>
          <ActionCard id={run.actionId} />
        </div>
      )}
      {run.pr?.url && (
        <p className="text-sm">
          Pull request: <a className="underline" href={run.pr.url} target="_blank" rel="noreferrer">{run.pr.url}</a>
          {run.pr.demo && <span className="text-gray-500"> (demo: nothing was pushed)</span>}
        </p>
      )}
      {run.error && <p className="text-sm text-red-600 dark:text-red-400">{run.error}</p>}
      {msg && <p className="text-sm text-red-600 dark:text-red-400">{msg}</p>}
    </Card>
  );
}

export default function EngineerTab() {
  const { token } = useAuth();
  const { coworker, refresh } = useCoworker();
  const api = coworkerApi(token);
  const [runs, setRuns] = useState<any[]>([]);
  const [reviews, setReviews] = useState<any[]>([]);
  const [ask, setAsk] = useState({ text: '', source: '', repo: '' });
  const [pr, setPr] = useState({ repo: '', number: '' });
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');
  const [settings, setSettings] = useState<Record<string, any>>({ default_repo: '', test_command: '', engineer_min_slop_score: 70 });
  const demo = coworker?.mode === 'demo';

  const load = async () => {
    const [r, v] = await Promise.all([api.get('/engineer/runs'), api.get('/reviews')]);
    setRuns(r.runs);
    setReviews(v.reviews);
  };
  useEffect(() => {
    load();
    const s = coworker?.settings || {};
    setSettings({ default_repo: s.default_repo || '', test_command: s.test_command || '', engineer_min_slop_score: s.engineer_min_slop_score ?? 70 });
  }, []);
  useEffect(() => {
    if (!runs.some((r) => r.status === 'running')) return;
    const t = setInterval(load, 3000);
    return () => clearInterval(t);
  }, [runs]);

  const replace = (run: any) => setRuns((rs) => rs.map((r) => (r.id === run.id ? run : r)));
  const act = async (fn: () => Promise<any>) => {
    setBusy(true);
    setMsg('');
    try {
      await fn();
      await load();
    } catch (e) {
      setMsg(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div>
      <Section title="Hand off engineering work"
        subtitle="Describe it, or point at a ticket. It confirms a spec, plans a task graph, writes the code, runs the tests, reviews itself, and opens a PR once you approve.">
        <Card className="p-4 space-y-2">
          <textarea className={`${inputCls} min-h-[80px]`} placeholder="What should it build? List acceptance criteria as bullets."
            value={ask.text} onChange={(e) => setAsk({ ...ask, text: e.target.value })} />
          <div className="grid sm:grid-cols-2 gap-2">
            <input className={inputCls} placeholder="…or a ticket: jira:ACME-142, notion:<page id>, github:owner/repo#12"
              value={ask.source} onChange={(e) => setAsk({ ...ask, source: e.target.value })} />
            <input className={inputCls} placeholder={settings.default_repo || 'owner/repo'} value={ask.repo}
              onChange={(e) => setAsk({ ...ask, repo: e.target.value })} />
          </div>
          <div className="flex gap-2 flex-wrap">
            <button className={primaryBtn} disabled={busy || (!ask.text.trim() && !ask.source.trim())}
              onClick={() => act(async () => {
                await api.post('/engineer/runs', ask);
                setAsk({ text: '', source: '', repo: '' });
              })}>
              Draft the spec
            </button>
            {demo && (
              <button className={ghostBtn} disabled={busy} onClick={() => act(() => api.post('/engineer/runs', { source: 'jira:ACME-142' }))}>
                Try the demo ticket (ACME-142)
              </button>
            )}
          </div>
        </Card>
      </Section>

      <Section title="Runs">
        {runs.length === 0 ? (
          <Empty title="No runs yet">Hand off a ticket above and watch each step here.</Empty>
        ) : (
          <div className="space-y-4">{runs.map((r) => <RunView key={r.id} run={r} onChange={replace} />)}</div>
        )}
      </Section>

      <Section title="AI code reviewer" subtitle="Reviews a pull request against your standards. The review is posted only when you approve it.">
        <Card className="p-4 space-y-3">
          <div className="flex gap-2">
            <input className={inputCls} placeholder={demo ? 'anote-demo/acme-api' : 'owner/repo'} value={pr.repo}
              onChange={(e) => setPr({ ...pr, repo: e.target.value })} />
            <input className={`${inputCls} max-w-[7rem]`} placeholder={demo ? '37' : 'PR #'} value={pr.number}
              onChange={(e) => setPr({ ...pr, number: e.target.value })} />
            <button className={primaryBtn} disabled={busy}
              onClick={() => act(() => api.post('/reviews', {
                repo: pr.repo || (demo ? 'anote-demo/acme-api' : ''), number: Number(pr.number || (demo ? 37 : 0)),
              }))}>
              Review
            </button>
          </div>
          {reviews.filter((r) => r.source === 'pr').slice(0, 5).map((r) => (
            <div key={r.id} className="border-t border-gray-100 dark:border-gray-700 pt-3">
              <p className="text-sm font-medium mb-1">{r.repo}#{r.number}</p>
              <Findings review={r} onDismiss={(id, scope) => act(() => api.post(`/reviews/${r.id}/findings/${id}/dismiss`, { scope }))} />
              {r.actionId && <ActionCard id={r.actionId} compact />}
            </div>
          ))}
        </Card>
      </Section>

      <Section title="Engineer settings">
        <Card className="p-4 grid sm:grid-cols-3 gap-3">
          <label className="text-sm">Default repository
            <input className={`${inputCls} mt-1`} placeholder="owner/repo" value={settings.default_repo}
              onChange={(e) => setSettings({ ...settings, default_repo: e.target.value })} />
          </label>
          <label className="text-sm">Test command
            <input className={`${inputCls} mt-1`} placeholder="detected (pytest, npm test, …)" value={settings.test_command}
              onChange={(e) => setSettings({ ...settings, test_command: e.target.value })} />
          </label>
          <label className="text-sm">Minimum slop score (below it, PRs always wait for you)
            <input className={`${inputCls} mt-1`} type="number" min={0} max={100} value={settings.engineer_min_slop_score}
              onChange={(e) => setSettings({ ...settings, engineer_min_slop_score: Number(e.target.value) })} />
          </label>
          <div className="sm:col-span-3">
            <button className={ghostBtn} disabled={busy} onClick={() => act(async () => {
              await api.patch('', { settings });
              await refresh();
              setMsg('Saved.');
            })}>
              Save
            </button>
          </div>
        </Card>
      </Section>
      {msg && <p className="text-sm text-gray-600 dark:text-gray-300">{msg}</p>}
    </div>
  );
}
