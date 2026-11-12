import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { API_BASE_URL } from "../constants/constants";

type Demo = { name: string; slug: string; sources: string[]; disclaimer: string };

export default function CompanyDemoPage() {
  const { slug = "" } = useParams();
  const [demo, setDemo] = useState<Demo | null>(null);
  const [error, setError] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    setDemo(null);
    fetch(`${API_BASE_URL}/api/demos/${encodeURIComponent(slug)}`)
      .then(async r => { if (!r.ok) throw new Error("This demo is unavailable."); return r.json(); })
      .then(setDemo).catch(e => setError(e.message));
  }, [slug]);
  async function ask(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || busy) return;
    setBusy(true); setError(""); setAnswer("");
    try {
      const r = await fetch(`${API_BASE_URL}/api/demos/${encodeURIComponent(slug)}/ask`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error || "Unable to answer");
      setAnswer(data.answer);
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to answer"); }
    finally { setBusy(false); }
  }
  return <main style={{maxWidth:760, margin:"4rem auto", padding:"1.5rem", fontFamily:"system-ui"}}>
    <p style={{color:"#666"}}>Ourogen · Company research demo</p>
    <h1>{demo ? `Explore ${demo.name}'s public information` : "Company chatbot"}</h1>
    {demo && <><p>{demo.disclaimer}</p><form onSubmit={ask}>
      <label htmlFor="question">Ask a question about the public sources</label>
      <textarea id="question" maxLength={500} rows={3} value={question}
        onChange={e => setQuestion(e.target.value)} style={{width:"100%",display:"block",margin:"1rem 0"}} />
      <button disabled={busy || !question.trim()} type="submit">{busy ? "Researching…" : "Ask"}</button>
    </form>{answer && <section aria-live="polite" style={{whiteSpace:"pre-wrap",marginTop:24}}>{answer}</section>}
    <h2>Public sources</h2><ul>{demo.sources.map((s,i) =>
      <li key={i}><a href={s} target="_blank" rel="noopener noreferrer">{s}</a></li>)}</ul>
    <p>Interested in private document intelligence? <a href="https://anote.ai/">Explore Anote</a>.</p></>}
    {error && <p role="alert">{error}</p>}
  </main>;
}
