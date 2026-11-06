import { useEffect, useState } from 'react';
import { useAuth } from '../../App';
import { coworkerApi, errorMessage } from '../api';
import { Card, Empty, Pill, Section, ghostBtn, inputCls, primaryBtn } from '../ui';

const ROLE_LABELS: Record<string, string> = {
  engineering: 'Engineering', sales: 'Sales', marketing: 'Marketing', healthcare: 'Healthcare operations',
  operations: 'Operations', assistant: 'Executive assistant',
};
const pct = (n: number | null) => (n === null || n === undefined ? '—' : `${Math.round(n * 100)}%`);

function Profile({ slug, onHire, busy }: { slug: string; onHire: () => void; busy: boolean }) {
  const { token } = useAuth();
  const api = coworkerApi(token);
  const [p, setP] = useState<any>(null);
  useEffect(() => {
    api.get(`/marketplace/ai/${slug}`).then(setP);
  }, [slug]);
  if (!p) return <div className="h-24 animate-pulse" />;
  return (
    <div className="mt-3 space-y-3 border-t border-gray-100 dark:border-gray-700 pt-3">
      <p className="text-xs text-gray-500">
        An AI built from {p.basedOn}'s work (knowledge pack v{p.packVersion}). It always says it's an AI. It works on your own
        data and connections, and {p.basedOn.split(' ')[0] || 'its creator'} never sees them.
      </p>
      <div className="grid sm:grid-cols-4 gap-2 text-sm">
        <div><p className="text-xs text-gray-500">Work done (30d)</p><p className="font-medium tabular-nums">{p.stats.workDone30d}</p></div>
        <div><p className="text-xs text-gray-500">Approved without edits</p><p className="font-medium">{pct(p.stats.acceptance)}</p></div>
        <div><p className="text-xs text-gray-500">Engineer runs passing</p><p className="font-medium">{pct(p.stats.engineerPassRate)}</p></div>
        <div><p className="text-xs text-gray-500">Rating</p><p className="font-medium">{p.stats.rating ? `${p.stats.rating}/5 (${p.stats.ratings})` : 'No ratings yet'}</p></div>
      </div>
      <div>
        <p className="text-xs font-medium text-gray-500 mb-1">Standards it holds code to</p>
        <ul className="list-disc pl-5 text-sm space-y-0.5">{p.styleRules.slice(0, 8).map((r: any) => <li key={r.id}>{r.text}</li>)}</ul>
      </div>
      <div className="flex flex-wrap gap-1.5">{p.playbooks.map((pb: any) => <Pill key={pb.id}>{pb.title}</Pill>)}</div>
      {p.reviews.length > 0 && (
        <ul className="text-sm space-y-1">{p.reviews.slice(0, 3).map((r: any, i: number) => <li key={i}>{'★'.repeat(r.rating)} {r.text}</li>)}</ul>
      )}
      <button className={primaryBtn} disabled={busy} onClick={onHire}>Hire for ${p.priceUsd}/month</button>
    </div>
  );
}

/** Hire other people's AIs, and publish your own. */
export default function MarketplaceTab() {
  const { token } = useAuth();
  const api = coworkerApi(token);
  const [listings, setListings] = useState<any[]>([]);
  const [me, setMe] = useState<any>(null);
  const [filter, setFilter] = useState({ role: '', q: '' });
  const [open, setOpen] = useState('');
  const [form, setForm] = useState<any>({ version: '', title: '', headline: '', role: 'engineering', priceUsd: 500, consent: '' });
  const [rating, setRating] = useState<Record<string, { rating: number; text: string }>>({});
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState('');

  const load = async () => {
    const [d, m] = await Promise.all([api.get('/marketplace', filter), api.get('/marketplace/me')]);
    setListings(d.listings);
    setMe(m);
    if (m.listing) setForm((f: any) => ({ ...f, title: m.listing.title, headline: m.listing.headline, role: m.listing.role, priceUsd: m.listing.priceUsd }));
    if (m.versions.length) setForm((f: any) => ({ ...f, version: f.version || m.versions[0] }));
  };
  useEffect(() => {
    load().catch((e) => setMsg(errorMessage(e)));
  }, [filter.role]);

  const act = async (fn: () => Promise<any>, done = '') => {
    setBusy(true);
    setMsg('');
    try {
      const out = await fn();
      if (out?.url) {
        window.location.href = out.url;
        return;
      }
      await load();
      setMsg(out?.note || done);
    } catch (e) {
      setMsg(errorMessage(e));
    } finally {
      setBusy(false);
    }
  };

  if (!me) return <div className="h-40 animate-pulse" />;
  const mine = me.listing;

  return (
    <div>
      <Section title="Hire an AI" subtitle="AIs built from real people's work: their skills, standards and playbooks, working on your data.">
        <div className="flex gap-2 mb-3">
          <select className={`${inputCls} max-w-[14rem]`} value={filter.role} onChange={(e) => setFilter({ ...filter, role: e.target.value })} aria-label="Role">
            <option value="">All roles</option>
            {Object.entries(ROLE_LABELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
          <input className={inputCls} placeholder="Search skills, e.g. Python, billing" value={filter.q}
            onChange={(e) => setFilter({ ...filter, q: e.target.value })} onKeyDown={(e) => e.key === 'Enter' && load()} />
          <button className={ghostBtn} onClick={load}>Search</button>
        </div>
        {listings.length === 0 ? <Empty title="No AIs listed yet">Publish yours below and be the first.</Empty> : (
          <div className="space-y-3">
            {listings.map((l) => (
              <Card key={l.slug} className="p-4">
                <button className="w-full text-left" onClick={() => setOpen(open === l.slug ? '' : l.slug)} aria-expanded={open === l.slug}>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-medium flex-1">{l.title}</span>
                    <Pill tone="blue">AI</Pill>
                    <Pill>{ROLE_LABELS[l.role] || l.role}</Pill>
                    <span className="text-sm tabular-nums">${l.priceUsd}/mo</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{l.headline || `Built from ${l.basedOn}'s work`} · {l.skills.join(', ')}</p>
                </button>
                {open === l.slug && <Profile slug={l.slug} busy={busy} onHire={() => act(() => api.post(`/marketplace/ai/${l.slug}/hire`))} />}
              </Card>
            ))}
          </div>
        )}
      </Section>

      {me.hires.length > 0 && (
        <Section title="Your hires" subtitle="While a hire is active, your AI engineer and code reviewer work from its knowledge pack.">
          <div className="space-y-2">
            {me.hires.map((h: any) => (
              <Card key={h.id} className="p-3">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium flex-1">{h.title}</span>
                  <Pill tone={h.status === 'active' ? 'green' : 'gray'}>{h.status}{h.status === 'active' && !h.paid ? ' · unpaid' : ''}</Pill>
                  {h.status === 'active' && <button className={ghostBtn} onClick={() => act(() => api.post(`/marketplace/hires/${h.id}/end`), 'Hire ended.')}>End</button>}
                </div>
                {h.status !== 'pending' && h.slug && (
                  <div className="flex gap-2 mt-2">
                    <select className={`${inputCls} max-w-[6rem]`} aria-label="Rating" value={rating[h.slug]?.rating || 5}
                      onChange={(e) => setRating({ ...rating, [h.slug]: { text: rating[h.slug]?.text || '', rating: Number(e.target.value) } })}>
                      {[5, 4, 3, 2, 1].map((n) => <option key={n} value={n}>{n} ★</option>)}
                    </select>
                    <input className={inputCls} placeholder="How did it do?" value={rating[h.slug]?.text || ''}
                      onChange={(e) => setRating({ ...rating, [h.slug]: { rating: rating[h.slug]?.rating || 5, text: e.target.value } })} />
                    <button className={ghostBtn} onClick={() => act(() => api.post(`/marketplace/ai/${h.slug}/rate`, rating[h.slug] || { rating: 5 }), 'Thanks for rating.')}>Rate</button>
                  </div>
                )}
              </Card>
            ))}
          </div>
        </Section>
      )}

      <Section title="Publish your AI" subtitle={`Let other teams hire your expertise. You keep ${Math.round(me.share * 100)}% of every hire. They never see your data, and you never see theirs.`}>
        {mine && (
          <Card className="p-4 mb-3">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-medium flex-1">{mine.title}</span>
              <Pill tone={mine.status === 'published' ? 'green' : 'gray'}>{mine.status}</Pill>
              <span className="text-sm">{me.activeHires} active hire(s) · ${me.monthlyEarningsUsd}/mo</span>
            </div>
            <div className="flex gap-2 mt-3">
              {!me.payoutsConnected && <button className={ghostBtn} onClick={() => act(() => api.post('/marketplace/payouts'))}>Set up payouts</button>}
              {mine.status === 'published' && (
                <button className={ghostBtn} onClick={() => act(() => api.post('/marketplace/unpublish'), 'Unpublished. Active hires have ended.')}>Unpublish</button>
              )}
            </div>
          </Card>
        )}
        {me.versions.length === 0 ? (
          <Empty title="Save a knowledge pack version first">Go to Knowledge, review what it learned, and click Save version.</Empty>
        ) : (
          <Card className="p-4 grid sm:grid-cols-2 gap-3">
            <label className="text-sm">Knowledge pack version
              <select className={`${inputCls} mt-1`} value={form.version} onChange={(e) => setForm({ ...form, version: Number(e.target.value) })}>
                {me.versions.map((v: number) => <option key={v} value={v}>Version {v}</option>)}
              </select>
            </label>
            <label className="text-sm">Role
              <select className={`${inputCls} mt-1`} value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
                {me.roles.map((r: string) => <option key={r} value={r}>{ROLE_LABELS[r] || r}</option>)}
              </select>
            </label>
            <label className="text-sm">Title<input className={`${inputCls} mt-1`} placeholder="AI Natan, billing engineer" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></label>
            <label className="text-sm">Price per month (USD)<input type="number" min={10} className={`${inputCls} mt-1`} value={form.priceUsd} onChange={(e) => setForm({ ...form, priceUsd: Number(e.target.value) })} /></label>
            <label className="text-sm sm:col-span-2">One line about it<input className={`${inputCls} mt-1`} value={form.headline} onChange={(e) => setForm({ ...form, headline: e.target.value })} /></label>
            <label className="text-sm sm:col-span-2">Type this to consent
              <p className="text-xs text-gray-500 my-1">“{me.consent}”</p>
              <input className={inputCls} value={form.consent} onChange={(e) => setForm({ ...form, consent: e.target.value })} />
            </label>
            <div className="sm:col-span-2">
              <button className={primaryBtn} disabled={busy || form.consent.trim() !== me.consent || !form.title.trim()}
                onClick={() => act(() => api.post('/marketplace/publish', form), 'Published.')}>
                {mine ? 'Update listing' : 'Publish'}
              </button>
            </div>
          </Card>
        )}
      </Section>
      {msg && <p className="text-sm text-gray-600 dark:text-gray-300">{msg}</p>}
    </div>
  );
}
