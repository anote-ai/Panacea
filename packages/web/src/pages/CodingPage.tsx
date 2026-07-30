import { useState } from "react";
import axios from "axios";
import { useAuth, useTheme } from "../App";
import RocketLogo from "../components/RocketLogo";

interface TreeNode {
  name: string;
  path: string;
  type: "dir" | "file";
  children?: TreeNode[];
}

function TreeItem({
  node,
  depth,
  selectedPath,
  onSelectFile,
}: {
  node: TreeNode;
  depth: number;
  selectedPath: string | null;
  onSelectFile: (path: string) => void;
}) {
  const [open, setOpen] = useState(depth === 0);

  if (node.type === "file") {
    return (
      <button
        onClick={() => onSelectFile(node.path)}
        className={`w-full text-left px-2 py-1 rounded-md text-sm truncate transition-colors ${
          selectedPath === node.path
            ? "bg-brand-blue-600 dark:bg-brand-blue-400 text-white dark:text-brand-blue-900"
            : "text-warm-text dark:text-warm-text-dark hover:bg-warm-border dark:hover:bg-warm-border-dark"
        }`}
        style={{ paddingLeft: `${depth * 14 + 8}px` }}
      >
        {node.name}
      </button>
    );
  }

  return (
    <div>
      {depth > 0 && (
        <button
          onClick={() => setOpen((o) => !o)}
          className="w-full text-left px-2 py-1 rounded-md text-sm font-medium text-warm-text dark:text-warm-text-dark hover:bg-warm-border dark:hover:bg-warm-border-dark transition-colors"
          style={{ paddingLeft: `${depth * 14 + 8}px` }}
        >
          {open ? "▾" : "▸"} {node.name}
        </button>
      )}
      {open &&
        node.children?.map((child) => (
          <TreeItem
            key={child.path || child.name}
            node={child}
            depth={depth + 1}
            selectedPath={selectedPath}
            onSelectFile={onSelectFile}
          />
        ))}
    </div>
  );
}

export default function CodingPage() {
  const { token } = useAuth();
  const { dark, toggle } = useTheme();

  const [repoUrl, setRepoUrl] = useState("");
  const [connecting, setConnecting] = useState(false);
  const [connectError, setConnectError] = useState<string | null>(null);
  const [tree, setTree] = useState<TreeNode | null>(null);
  const [repoId, setRepoId] = useState<string | null>(null);

  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string | null>(null);
  const [fileLoading, setFileLoading] = useState(false);
  const [fileError, setFileError] = useState<string | null>(null);

  const connectRepo = async () => {
    if (!repoUrl.trim()) return;
    setConnecting(true);
    setConnectError(null);
    setTree(null);
    setRepoId(null);
    setSelectedPath(null);
    setFileContent(null);
    try {
      const res = await axios.post(
        "/api/coding/connect-repo",
        { repoUrl: repoUrl.trim() },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRepoId(res.data.repoId);
      setTree(res.data.tree);
    } catch (err: any) {
      setConnectError(err.response?.data?.error || "Failed to connect to repo.");
    } finally {
      setConnecting(false);
    }
  };

  const selectFile = async (path: string) => {
    if (!repoId) return;
    setSelectedPath(path);
    setFileLoading(true);
    setFileError(null);
    setFileContent(null);
    try {
      const res = await axios.get(`/api/coding/repos/${repoId}/file`, {
        params: { path },
        headers: { Authorization: `Bearer ${token}` },
      });
      setFileContent(res.data.content);
    } catch (err: any) {
      setFileError(err.response?.data?.error || "Failed to load file.");
    } finally {
      setFileLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-warm-bg dark:bg-warm-bg-dark text-warm-text dark:text-warm-text-dark">
      <div className="flex items-center justify-between px-6 py-4 border-b border-warm-border dark:border-warm-border-dark">
        <div className="flex items-center gap-2">
          <RocketLogo className="w-7 h-7" />
          <span className="font-semibold">Panacea Coding Workspace</span>
        </div>
        <button
          onClick={toggle}
          className="p-2 rounded-lg hover:bg-warm-card dark:hover:bg-warm-card-dark text-warm-muted dark:text-warm-muted-dark"
          aria-label="Toggle theme"
        >
          {dark ? "☀️" : "🌙"}
        </button>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="flex gap-2">
          <input
            type="text"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && connectRepo()}
            placeholder="https://github.com/owner/repo"
            className="flex-1 px-4 py-3 rounded-lg border border-warm-border dark:border-warm-border-dark bg-warm-card dark:bg-warm-card-dark text-warm-text dark:text-warm-text-dark placeholder-warm-muted dark:placeholder-warm-muted-dark focus:outline-none focus:ring-2 focus:ring-warm-border dark:focus:ring-warm-border-dark"
          />
          <button
            onClick={connectRepo}
            disabled={connecting || !repoUrl.trim()}
            className="px-6 py-3 rounded-lg font-medium bg-brand-blue-600 dark:bg-brand-blue-400 text-white dark:text-brand-blue-900 hover:bg-brand-blue-800 dark:hover:bg-brand-blue-200 disabled:opacity-50 transition-colors"
          >
            {connecting ? "Connecting..." : "Connect"}
          </button>
        </div>
        {connectError && <p className="mt-2 text-sm text-red-500">{connectError}</p>}

        {tree && (
          <div className="mt-6 grid md:grid-cols-[280px,1fr] gap-6">
            <div className="rounded-xl border border-warm-border dark:border-warm-border-dark bg-warm-card dark:bg-warm-card-dark p-2 max-h-[70vh] overflow-auto">
              <TreeItem node={tree} depth={0} selectedPath={selectedPath} onSelectFile={selectFile} />
            </div>

            <div className="rounded-xl border border-warm-border dark:border-warm-border-dark bg-warm-card dark:bg-warm-card-dark p-4 max-h-[70vh] overflow-auto">
              {!selectedPath && (
                <p className="text-sm text-warm-muted dark:text-warm-muted-dark">
                  Select a file to view its contents.
                </p>
              )}
              {selectedPath && fileLoading && (
                <p className="text-sm text-warm-muted dark:text-warm-muted-dark">Loading file...</p>
              )}
              {selectedPath && !fileLoading && fileError && (
                <p className="text-sm text-red-500">{fileError}</p>
              )}
              {selectedPath && !fileLoading && !fileError && fileContent !== null && (
                <pre className="whitespace-pre-wrap text-sm">{fileContent}</pre>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
