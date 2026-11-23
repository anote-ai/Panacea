import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { API_BASE_URL } from '../constants/constants';

type Details = { title: string; ownerName: string; coworkerName: string; status: string; platform: string };

export default function MeetingConsentPage() {
  const { token = '' } = useParams();
  const endpoint = `${API_BASE_URL}/api/coworker/meetings/consent/${encodeURIComponent(token)}`;
  const [details, setDetails] = useState<Details | null>(null);
  const [confirmed, setConfirmed] = useState(false);
  const [result, setResult] = useState<'agreed' | 'declined' | 'unavailable' | ''>('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    axios.get(endpoint).then((r) => {
      setDetails(r.data);
      if (['consent_granted', 'active', 'starting'].includes(r.data.status)) setResult('agreed');
      if (r.data.status === 'declined') setResult('declined');
      if (r.data.status === 'ended' || r.data.status === 'failed') setResult('unavailable');
    }).catch((e) => setError(e?.response?.data?.error || 'This consent link is unavailable.'));
  }, [endpoint]);

  const decide = async (decision: 'agree' | 'decline') => {
    setBusy(true);
    setError('');
    try {
      await axios.post(endpoint, { decision });
      setResult(decision === 'agree' ? 'agreed' : 'declined');
    } catch (e: any) {
      setError(e?.response?.data?.error || 'We could not save your response.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="min-h-screen bg-[#F7F7F8] dark:bg-[#171717] text-gray-900 dark:text-gray-100 flex items-center justify-center px-4 py-10">
      <section className="w-full max-w-lg rounded-2xl bg-white dark:bg-[#212121] border border-gray-200 dark:border-gray-700 p-6 sm:p-8 shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <img src="/ourogen-icon-black.png" alt="" className="h-9 w-9 dark:invert" />
          <div><p className="font-semibold">Ourogen Coworker</p><p className="text-xs text-gray-500">Meeting consent</p></div>
        </div>
        {error && !details ? <p className="text-sm text-red-600">{error}</p> : !details ? <p className="text-sm text-gray-500">Loading meeting…</p> : result ? (
          <div className="space-y-3">
            <h1 className="text-xl font-semibold">{result === 'agreed' ? 'Consent recorded' : result === 'declined' ? 'Request declined' : 'Request closed'}</h1>
            <p className="text-sm text-gray-600 dark:text-gray-300">
              {result === 'agreed'
                ? `${details.ownerName}'s disclosed AI coworker can now join. You can ask it to stop or leave at any time.`
                : result === 'declined' ? 'The AI coworker will not join this meeting.' : 'This consent request is no longer active.'}
            </p>
            <p className="text-sm text-gray-500">You may close this page.</p>
          </div>
        ) : (
          <div className="space-y-5">
            <div><h1 className="text-xl font-semibold">AI coworker requested for this meeting</h1><p className="mt-1 text-sm text-gray-500">{details.title}</p></div>
            <div className="rounded-xl bg-[#F7F7F8] dark:bg-[#2F2F2F] p-4 text-sm space-y-2">
              <p><strong>{details.ownerName}</strong> wants to send <strong>{details.coworkerName}</strong>, a disclosed AI participant.</p>
              <p>It will process live meeting audio through Ourogen's meeting and voice providers, create notes and a transcript, answer questions, and prepare follow-up work.</p>
              <p>Anyone can ask it to stop or leave during the meeting.</p>
            </div>
            <label className="flex items-start gap-3 text-sm cursor-pointer">
              <input type="checkbox" className="mt-1" checked={confirmed} onChange={(e) => setConfirmed(e.target.checked)} />
              <span>I agree, and I confirm that everyone joining this meeting has agreed to the disclosed AI coworker processing the conversation and taking notes.</span>
            </label>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <div className="flex flex-col sm:flex-row gap-2">
              <button disabled={!confirmed || busy} onClick={() => decide('agree')} className="rounded-lg bg-black dark:bg-white text-white dark:text-black px-4 py-2.5 text-sm font-medium disabled:opacity-40">Agree and allow it to join</button>
              <button disabled={busy} onClick={() => decide('decline')} className="rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2.5 text-sm">Decline</button>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
