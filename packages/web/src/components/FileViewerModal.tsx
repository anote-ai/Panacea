import axios from 'axios';
import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface ViewableDoc {
  id: string;
  filename: string;
}

interface Props {
  doc: ViewableDoc | null;
  token: string | null;
  onClose: () => void;
}

export default function FileViewerModal({ doc, token, onClose }: Props) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileUrl, setFileUrl] = useState<string | null>(null);
  const [textContent, setTextContent] = useState<string | null>(null);
  const [htmlContent, setHtmlContent] = useState<string | null>(null);

  const ext = doc ? doc.filename.split('.').pop()?.toLowerCase() : undefined;

  useEffect(() => {
    if (!doc) return;
    let objectUrl: string | null = null;
    let cancelled = false;

    setLoading(true);
    setError(null);
    setFileUrl(null);
    setTextContent(null);
    setHtmlContent(null);

    (async () => {
      try {
        const res = await axios.get(`/api/documents/${doc.id}/file`, {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob',
        });
        if (cancelled) return;
        const blob = res.data as Blob;

        if (ext === 'docx') {
          const mammoth = await import('mammoth');
          const arrayBuffer = await blob.arrayBuffer();
          const result = await mammoth.convertToHtml({ arrayBuffer });
          if (!cancelled) setHtmlContent(result.value);
        } else if (ext === 'txt' || ext === 'md' || ext === 'csv') {
          const text = await blob.text();
          if (!cancelled) setTextContent(text);
        } else {
          objectUrl = URL.createObjectURL(blob);
          if (!cancelled) setFileUrl(objectUrl);
        }
      } catch {
        if (!cancelled) setError('Failed to load file preview.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();

    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [doc, token, ext]);

  if (!doc) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4 py-8"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-[#2F2F2F] rounded-2xl shadow-xl w-full max-w-3xl h-full max-h-[85vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
          <h2
            className="text-sm font-semibold truncate pr-4 text-gray-900 dark:text-white"
            title={doc.filename}
          >
            {doc.filename}
          </h2>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-[#3F3F3F] transition-colors flex-shrink-0"
            aria-label="Close"
          >
            ✕
          </button>
        </div>
        <div className="flex-1 overflow-auto">
          {loading && (
            <div className="flex items-center justify-center h-full text-sm text-gray-400 dark:text-gray-500">
              Loading preview...
            </div>
          )}
          {!loading && error && (
            <div className="flex items-center justify-center h-full text-sm text-red-500">
              {error}
            </div>
          )}
          {!loading && !error && ext === 'pdf' && fileUrl && (
            <iframe
              src={fileUrl}
              title={doc.filename}
              className="w-full h-full border-0"
            />
          )}
          {!loading && !error && (ext === 'txt' || ext === 'csv') && textContent !== null && (
            <pre className="whitespace-pre-wrap text-sm p-4 text-gray-900 dark:text-white">
              {textContent}
            </pre>
          )}
          {!loading && !error && ext === 'md' && textContent !== null && (
            <div className="prose prose-sm dark:prose-invert max-w-none p-4">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{textContent}</ReactMarkdown>
            </div>
          )}
          {!loading && !error && ext === 'docx' && htmlContent !== null && (
            <div
              className="prose prose-sm dark:prose-invert max-w-none p-4"
              dangerouslySetInnerHTML={{ __html: htmlContent }}
            />
          )}
          {!loading && !error && fileUrl && ext !== 'pdf' && (
            <div className="flex flex-col items-center justify-center h-full gap-3 text-sm text-gray-400 dark:text-gray-500">
              <p>Preview not available for this file type.</p>
              <a
                href={fileUrl}
                download={doc.filename}
                className="px-3 py-1.5 rounded-lg bg-gray-900 dark:bg-white text-white dark:text-gray-900 text-xs font-medium"
              >
                Download
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
