import axios from 'axios';
import { useEffect, useRef, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Link } from 'react-router-dom';
import remarkGfm from 'remark-gfm';
import RocketLogo from '../components/RocketLogo';
import { useTheme } from '../App';

interface DemoDoc {
  id: string;
  name: string;
  category: string;
  suggestedQuestions: string[];
}

interface DemoSource {
  chunk: string;
  docId: string;
  docName: string;
  score: number;
}

interface DemoMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: DemoSource[];
}

function SourceList({ sources }: { sources: DemoSource[] }) {
  const [open, setOpen] = useState(false);
  if (!sources.length) return null;
  return (
    <div className="mt-3 border-t border-gray-200 dark:border-gray-700 pt-2">
      <button
        onClick={() => setOpen((v) => !v)}
        className="text-xs font-medium text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
      >
        {open ? '▾' : '▸'} Sources ({sources.length})
      </button>
      {open && (
        <ul className="mt-2 space-y-2">
          {sources.map((s, i) => (
            <li key={i} className="rounded-lg bg-[#F7F7F8] dark:bg-[#212121] p-3 text-xs">
              <div className="flex items-center justify-between gap-2 mb-1">
                <span className="font-medium truncate">{s.docName}</span>
                <span className="text-gray-400 dark:text-gray-500 flex-shrink-0">
                  relevance {Math.round(s.score * 100)}%
                </span>
              </div>
              <p className="text-gray-600 dark:text-gray-300 whitespace-pre-wrap line-clamp-6">
                {s.chunk}
              </p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function DemoPage() {
  const { dark, toggle } = useTheme();
  const [docs, setDocs] = useState<DemoDoc[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);
  const [messages, setMessages] = useState<DemoMessage[]>([]);
  const [input, setInput] = useState('');
  const [remaining, setRemaining] = useState<number | null>(null);
  const [limit, setLimit] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    axios
      .get('/api/demo/documents')
      .then((res) => {
        setDocs(res.data.documents || []);
        setRemaining(res.data.remaining ?? 5);
        setLimit(res.data.questionLimit ?? 5);
      })
      .catch(() => setError('The demo backend is not reachable right now.'));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const outOfQuestions = remaining !== null && remaining <= 0;

  const ask = async (question: string) => {
    const q = question.trim();
    if (!q || loading || outOfQuestions) return;
    setInput('');
    setError(null);
    setMessages((m) => [...m, { role: 'user', content: q }]);
    setLoading(true);
    try {
      const res = await axios.post('/api/demo/ask', {
        question: q,
        docId: selectedDoc || undefined,
      });
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: res.data.answer, sources: res.data.sources },
      ]);
      setRemaining(res.data.remaining);
    } catch (e: any) {
      if (e?.response?.status === 429) {
        setRemaining(0);
      } else {
        setError('Something went wrong answering that question. Please try again.');
        setMessages((m) => m.slice(0, -1));
      }
    } finally {
      setLoading(false);
    }
  };

  const used = remaining === null ? 0 : limit - remaining;

  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-[#212121] text-gray-900 dark:text-white">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <RocketLogo className="w-6 h-6" />
          Anote
          <span className="ml-2 text-xs font-medium px-2 py-0.5 rounded-full bg-[#F7F7F8] dark:bg-[#2F2F2F] text-gray-500 dark:text-gray-400">
            Live demo — no sign-up
          </span>
        </Link>
        <div className="flex items-center gap-3">
          <button
            onClick={toggle}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-[#2F2F2F] transition-colors"
            aria-label="Toggle theme"
          >
            {dark ? '☀️' : '🌙'}
          </button>
          <Link
            to="/register"
            className="px-4 py-2 rounded-lg text-sm font-medium bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
          >
            Sign up free
          </Link>
        </div>
      </header>

      <div className="flex-1 flex flex-col lg:flex-row max-w-6xl w-full mx-auto">
        {/* Document picker */}
        <aside className="lg:w-72 flex-shrink-0 p-4 lg:border-r border-gray-200 dark:border-gray-700">
          <h2 className="text-sm font-semibold mb-3">Sample documents</h2>
          <button
            onClick={() => setSelectedDoc(null)}
            className={`w-full text-left mb-2 rounded-xl border p-3 text-sm transition-colors ${
              selectedDoc === null
                ? 'border-gray-900 dark:border-white bg-[#F7F7F8] dark:bg-[#2F2F2F]'
                : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-[#2F2F2F]'
            }`}
          >
            All documents
          </button>
          {docs.map((doc) => (
            <button
              key={doc.id}
              onClick={() => setSelectedDoc(doc.id)}
              className={`w-full text-left mb-2 rounded-xl border p-3 transition-colors ${
                selectedDoc === doc.id
                  ? 'border-gray-900 dark:border-white bg-[#F7F7F8] dark:bg-[#2F2F2F]'
                  : 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-[#2F2F2F]'
              }`}
            >
              <div className="text-xs font-medium text-gray-400 dark:text-gray-500 mb-0.5">
                {doc.category}
              </div>
              <div className="text-sm font-medium leading-snug">{doc.name}</div>
            </button>
          ))}
        </aside>

        {/* Chat area */}
        <main className="flex-1 flex flex-col p-4 min-h-0">
          <div className="flex-1 overflow-y-auto">
            {messages.length === 0 && (
              <div className="mt-8 text-center">
                <h1 className="text-2xl font-bold">Ask these documents anything</h1>
                <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                  {limit} free questions, answered with source citations. No account needed.
                </p>
                <div className="mt-6 flex flex-wrap justify-center gap-2 max-w-xl mx-auto">
                  {(selectedDoc
                    ? docs.filter((d) => d.id === selectedDoc)
                    : docs
                  ).flatMap((d) =>
                    d.suggestedQuestions.map((q) => (
                      <button
                        key={`${d.id}-${q}`}
                        onClick={() => ask(q)}
                        disabled={outOfQuestions || loading}
                        className="px-3 py-1.5 rounded-full border border-gray-300 dark:border-gray-600 text-sm hover:bg-gray-100 dark:hover:bg-[#2F2F2F] disabled:opacity-40 transition-colors"
                      >
                        {q}
                      </button>
                    ))
                  )}
                </div>
              </div>
            )}

            <div className="space-y-4 py-2">
              {messages.map((msg, i) =>
                msg.role === 'user' ? (
                  <div key={i} className="flex justify-end">
                    <div className="max-w-[85%] rounded-2xl bg-[#F7F7F8] dark:bg-[#2F2F2F] px-4 py-2.5 text-sm">
                      {msg.content}
                    </div>
                  </div>
                ) : (
                  <div key={i} className="max-w-[95%]">
                    <div className="rounded-2xl border border-gray-200 dark:border-gray-700 px-4 py-3 text-sm prose prose-sm dark:prose-invert max-w-none">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                      <SourceList sources={msg.sources || []} />
                    </div>
                  </div>
                )
              )}
              {loading && (
                <div className="text-sm text-gray-400 dark:text-gray-500 animate-pulse">
                  Reading the documents…
                </div>
              )}
              <div ref={bottomRef} />
            </div>
          </div>

          {/* Sign-up gate */}
          {outOfQuestions && (
            <div className="mb-3 rounded-2xl border border-gray-300 dark:border-gray-600 bg-[#F7F7F8] dark:bg-[#2F2F2F] p-4 text-center">
              <p className="font-medium">You've used all {limit} free questions</p>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Create a free account to keep asking — and to upload your own documents.
              </p>
              <Link
                to="/register"
                className="inline-block mt-3 px-5 py-2.5 rounded-lg font-medium bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
              >
                Sign up free
              </Link>
            </div>
          )}

          {error && (
            <div className="mb-3 text-sm text-red-500 text-center">{error}</div>
          )}

          {/* Input */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              ask(input);
            }}
            className="flex items-end gap-2 rounded-2xl border border-gray-300 dark:border-gray-600 bg-[#F7F7F8] dark:bg-[#2F2F2F] p-2"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                outOfQuestions
                  ? 'Sign up to keep asking questions'
                  : selectedDoc
                    ? `Ask about ${docs.find((d) => d.id === selectedDoc)?.name ?? 'this document'}…`
                    : 'Ask a question about the sample documents…'
              }
              disabled={outOfQuestions || loading}
              maxLength={500}
              className="flex-1 bg-transparent px-2 py-2 text-sm outline-none disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading || outOfQuestions}
              className="p-2 rounded-lg bg-gray-900 dark:bg-white text-white dark:text-gray-900 hover:bg-gray-800 dark:hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              aria-label="Send question"
            >
              ↑
            </button>
          </form>
          {remaining !== null && !outOfQuestions && (
            <p className="mt-2 text-xs text-center text-gray-400 dark:text-gray-500">
              {used} of {limit} free questions used
            </p>
          )}
        </main>
      </div>
    </div>
  );
}
