import { useEffect, useState } from 'react';
import { useAuth } from '../../App';
import { coworkerApi, errorMessage } from '../api';
import { Card, Section, ghostBtn } from '../ui';

const OUTPUT_LABELS: Record<string, string> = {
  prsOpened: 'PRs opened', prsMerged: 'PRs merged', prsReviewed: 'PRs reviewed', engineerRuns: 'Engineer runs',
  ticketsShipped: 'Tickets shipped', emails: 'Emails sent', slackPosts: 'Slack posts', invites: 'Invites sent',
  crmUpdates: 'CRM updates', meetings: 'Meetings covered', briefs: 'Briefs', taskRuns: 'Scheduled task runs',
  reviewsPosted: 'Reviews posted', comments: 'Comments', issuesFiled: 'Issues filed', ticketsFiled: 'Tickets filed',
  docsWritten: 'Docs written', toolCalls: 'Tool calls',
};
const RANGES = [{ days: 1, label: 'Today' }, { days: 7, label: '7 days' }, { days: 30, label: '30 days' }];

const money = (n: number) => `$${n.toLocaleString(undefined, { maximumFractionDigits: n < 100 ? 2 : 0 })}`;
const pct = (n: number | null | undefined) => (n === null || n === undefined ? '—' : `${Math.round(n * 100)}%`);

function Tile({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <Card className="p-4">
      <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold tabular-nums">{value}</p>
      {note && <p className="mt-1 text-[11px] text-gray-500 dark:text-gray-400">{note}</p>}
    </Card>
  );
}

/** Work done per unit of time: what it shipped, how good it was, and what it cost next to a hire. */
export default function ScorecardTab() {
  const { token } = useAuth();
  const api = coworkerApi(token);
  const [days, setDays] = useState(7);
  const [card, setCard] = useState<any>(null);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    setCard(null);
    api.get('/scorecard', { days }).then(setCard).catch((e) => setMsg(errorMessage(e)));
  }, [days]);

  const download = async () => {
    try {
      const res = await fetch(`${api.base}/scorecard?days=${days}&format=csv`, { headers: api.headers });
      const url = URL.createObjectURL(await res.blob());
      const a = document.createElement('a');
      a.href = url;
      a.download = `scorecard-${days}d.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setMsg(errorMessage(e));
    }
  };

  const range = (
    <div className="flex gap-1" role="group" aria-label="Time range">
      {RANGES.map((r) => (
        <button key={r.days} onClick={() => setDays(r.days)} aria-pressed={days === r.days}
          className={`px-3 py-1.5 rounded-lg text-sm ${days === r.days ? 'bg-black text-white dark:bg-white dark:text-black' : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/10'}`}>
          {r.label}
        </button>
      ))}
      <button className={ghostBtn} onClick={download}>CSV</button>
    </div>
  );

  if (!card) return <Section title="Scorecard" action={range}>{msg ? <p className="text-sm text-red-600">{msg}</p> : <div className="h-40 animate-pulse" />}</Section>;
  const out = Object.entries(card.output as Record<string, number>).filter(([, n]) => n > 0);
  const vs = card.vsHire;

  return (
    <div>
      <Section title="Scorecard" subtitle="Work done per unit of time. Everything marked as an estimate is one." action={range}>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Tile label="Work done" value={String(card.totalOutput)} note={`${card.rates.perDay} a day`} />
          <Tile label="Your attention" value={`${card.humanAttentionHours}h`}
            note={card.rates.perHumanHour ? `${card.rates.perHumanHour} pieces per hour of yours (estimate)` : 'Estimate'} />
          <Tile label="Active hours" value={String(card.activeHours)} note="Hours it was doing something" />
          <Tile label="Hours saved" value={`${card.hoursSaved}h`} note="Estimate from the work done" />
        </div>
      </Section>

      <Section title="What it shipped">
        {out.length === 0 ? (
          <p className="text-sm text-gray-500">Nothing yet in this range. Hand it a ticket or a responsibility.</p>
        ) : (
          <Card className="divide-y divide-gray-100 dark:divide-gray-700">
            {out.map(([k, n]) => (
              <div key={k} className="flex justify-between px-4 py-2 text-sm">
                <span>{OUTPUT_LABELS[k] || k}</span>
                <span className="tabular-nums font-medium">{n}</span>
              </div>
            ))}
          </Card>
        )}
      </Section>

      <Section title="Quality">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Tile label="Approved without edits" value={pct(card.quality.acceptance)} />
          <Tile label="Edits per approval" value={card.quality.editsPerApproval ?? '—'} />
          <Tile label="Undone" value={String(card.quality.reverts)} />
          <Tile label="Engineer runs passing" value={pct(card.quality.engineerPassRate)}
            note={card.quality.avgSlopScore !== null ? `Average slop score ${card.quality.avgSlopScore}/100` : undefined} />
        </div>
      </Section>

      <Section title="Cost, next to a hire" subtitle={card.notes.vsHire}>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <Tile label="AI cost" value={money(card.cost.totalUsd)} note={`Plan ${money(card.cost.planUsd)} + models ${money(card.cost.modelUsd)}`} />
          <Tile label={`${vs.roleLabel}, same period`} value={money(vs.hireCostUsd)} note={`${money(vs.annualSalaryUsd)}/year benchmark`} />
          <Tile label="AI cost vs hire" value={vs.costRatio === null ? '—' : `${(vs.costRatio * 100).toFixed(1)}%`} />
          <Tile label="Work value" value={money(vs.workValueUsd)} note="Hours saved × the role's hourly cost (estimate)" />
        </div>
        <p className="mt-2 text-xs text-gray-500">Change the role in Settings → Identity & preferences.</p>
      </Section>

      {Object.keys(card.quality.evals || {}).length > 0 && (
        <Section title="Latest eval scores" subtitle="Offline evals, run in CI on every change.">
          <Card className="divide-y divide-gray-100 dark:divide-gray-700">
            {Object.entries(card.quality.evals as Record<string, number>).map(([k, v]) => (
              <div key={k} className="flex justify-between px-4 py-2 text-sm">
                <span className="font-mono text-xs">{k}</span>
                <span className="tabular-nums">{pct(v)}</span>
              </div>
            ))}
          </Card>
        </Section>
      )}
      {msg && <p className="text-sm text-red-600">{msg}</p>}
    </div>
  );
}
