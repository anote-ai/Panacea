import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../App';
import DocThumbnail from '../components/DocThumbnail';
import FileViewerModal from '../components/FileViewerModal';
import RocketLogo from '../components/RocketLogo';
import UserMenu from '../components/UserMenu';
import { API_BASE_URL } from '../constants/constants';
interface Folder {
  id: number;
  name: string;
}
interface Document {
  id: string;
  filename: string;
  chunks: number;
  folder_id: number | null;
  chat_id: number | null;
  chat_name?: string | null;
}
interface RubberBand {
  startX: number;
  startY: number;
  curX: number;
  curY: number;
}

export default function DocumentsPage() {
  const { token } = useAuth();
  const nav = useNavigate();

  const [folders, setFolders] = useState<Folder[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<Folder | null>(null);
  const [draggingDoc, setDraggingDoc] = useState<string | null>(null);
  const [draggingOver, setDraggingOver] = useState<number | 'root' | null>(
    null,
  );
  const [newFolderName, setNewFolderName] = useState('');
  const [creatingFolder, setCreatingFolder] = useState(false);
  const [renamingId, setRenamingId] = useState<number | null>(null);
  const [renameValue, setRenameValue] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Multi-select state
  const [selectedDocs, setSelectedDocs] = useState<Set<string>>(new Set());
  const [rubberBand, setRubberBand] = useState<RubberBand | null>(null);
  const [lastClickedId, setLastClickedId] = useState<string | null>(null);
  const [bulkMoveFolder, setBulkMoveFolder] = useState<string>('');
  const [viewingDoc, setViewingDoc] = useState<Document | null>(null);

  const listRef = useRef<HTMLDivElement>(null);
  const docItemRefs = useRef<Map<string, HTMLDivElement>>(new Map());
  const isRubberBanding = useRef(false);

  const headers = { Authorization: `Bearer ${token}` };

  const loadFolders = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/folders`, { headers });
      setFolders(res.data.folders || []);
    } catch {}
  }, [token]);

  const loadDocuments = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/documents`, { headers });
      setDocuments(res.data.documents || []);
    } catch {}
  }, [token]);

  useEffect(() => {
    loadFolders();
  }, [loadFolders]);
  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);
  useEffect(() => {
    setSelectedDocs(new Set());
  }, [selectedFolder]);

  // Rubber-band mouse events on window
  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      if (!isRubberBanding.current || !rubberBand || !listRef.current) return;
      const rect = listRef.current.getBoundingClientRect();
      const curX = e.clientX - rect.left;
      const curY = e.clientY - rect.top + listRef.current.scrollTop;
      setRubberBand((rb) => (rb ? { ...rb, curX, curY } : null));

      // Determine which docs intersect the rubber band
      const minX = Math.min(rubberBand.startX, curX);
      const maxX = Math.max(rubberBand.startX, curX);
      const minY = Math.min(rubberBand.startY, curY);
      const maxY = Math.max(rubberBand.startY, curY);

      const hit = new Set<string>();
      docItemRefs.current.forEach((el, id) => {
        const r = el.getBoundingClientRect();
        const elTop = r.top - rect.top + listRef.current!.scrollTop;
        const elBottom = elTop + r.height;
        const elLeft = r.left - rect.left;
        const elRight = elLeft + r.width;
        if (
          elLeft < maxX &&
          elRight > minX &&
          elTop < maxY &&
          elBottom > minY
        ) {
          hit.add(id);
        }
      });
      setSelectedDocs(hit);
    };

    const onMouseUp = () => {
      if (isRubberBanding.current) {
        isRubberBanding.current = false;
        setRubberBand(null);
      }
    };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    return () => {
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
    };
  }, [rubberBand]);

  const onListMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (draggingDoc) return;
    // Only start rubber band when clicking directly on the list background
    const target = e.target as HTMLElement;
    if (target.closest('[data-doc-item]')) return;
    if (!listRef.current) return;
    const rect = listRef.current.getBoundingClientRect();
    const startX = e.clientX - rect.left;
    const startY = e.clientY - rect.top + listRef.current.scrollTop;
    isRubberBanding.current = true;
    setRubberBand({ startX, startY, curX: startX, curY: startY });
    if (!e.shiftKey && !e.ctrlKey && !e.metaKey) setSelectedDocs(new Set());
  };

  const onDocClick = (
    e: React.MouseEvent,
    docId: string,
    displayDocs: Document[],
  ) => {
    e.stopPropagation();
    if (e.shiftKey && lastClickedId) {
      // Range select
      const ids = displayDocs.map((d) => d.id);
      const a = ids.indexOf(lastClickedId);
      const b = ids.indexOf(docId);
      const range = ids.slice(Math.min(a, b), Math.max(a, b) + 1);
      setSelectedDocs((prev) => new Set([...prev, ...range]));
    } else if (e.ctrlKey || e.metaKey) {
      // Toggle
      setSelectedDocs((prev) => {
        const next = new Set(prev);
        next.has(docId) ? next.delete(docId) : next.add(docId);
        return next;
      });
    } else {
      // Single select (or deselect if already only this one)
      setSelectedDocs((prev) =>
        prev.size === 1 && prev.has(docId) ? new Set() : new Set([docId]),
      );
    }
    setLastClickedId(docId);
  };

  const createFolder = async () => {
    const name = newFolderName.trim();
    if (!name) return;
    try {
      const res = await axios.post(`${API_BASE_URL}/api/folders`, { name }, { headers });
      setFolders((prev) => [...prev, res.data]);
      setNewFolderName('');
      setCreatingFolder(false);
    } catch {}
  };

  const renameFolder = async (id: number) => {
    const name = renameValue.trim();
    if (!name) {
      setRenamingId(null);
      return;
    }
    try {
      await axios.patch(`${API_BASE_URL}/api/folders/${id}`, { name }, { headers });
      setFolders((prev) => prev.map((f) => (f.id === id ? { ...f, name } : f)));
      if (selectedFolder?.id === id)
        setSelectedFolder((f) => (f ? { ...f, name } : f));
    } catch {}
    setRenamingId(null);
  };

  const deleteFolder = async (id: number) => {
    if (!confirm('Delete this folder? Documents inside will become unfiled.'))
      return;
    try {
      await axios.delete(`${API_BASE_URL}/api/folders/${id}`, { headers });
      setFolders((prev) => prev.filter((f) => f.id !== id));
      if (selectedFolder?.id === id) setSelectedFolder(null);
      loadDocuments();
    } catch {}
  };

  const deleteDocument = async (docId: string) => {
    try {
      await axios.delete(`/api/documents/${docId}`, { headers });
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
      setSelectedDocs((prev) => {
        const n = new Set(prev);
        n.delete(docId);
        return n;
      });
    } catch {}
  };

  const deleteSelected = async () => {
    if (
      !confirm(
        `Delete ${selectedDocs.size} document${selectedDocs.size > 1 ? 's' : ''}?`,
      )
    )
      return;
    await Promise.all(Array.from(selectedDocs).map(deleteDocument));
    setSelectedDocs(new Set());
  };

  const moveDocument = async (docId: string, folderId: number | null) => {
    try {
      await axios.patch(
        `${API_BASE_URL}/api/documents/${docId}/move`,
        { folder_id: folderId },
        { headers },
      );
      setDocuments((prev) =>
        prev.map((d) => (d.id === docId ? { ...d, folder_id: folderId } : d)),
      );
      loadDocuments();
    } catch {}
  };

  const moveSelected = async (folderId: number | null) => {
    await Promise.all(
      Array.from(selectedDocs).map((id) => moveDocument(id, folderId)),
    );
    setSelectedDocs(new Set());
    setBulkMoveFolder('');
  };

  const onDocDragStart = (docId: string) => {
    setDraggingDoc(docId);
    isRubberBanding.current = false;
    setRubberBand(null);
  };
  const onDocDragEnd = () => {
    setDraggingDoc(null);
    setDraggingOver(null);
  };
  const onFolderDragOver = (e: React.DragEvent, target: number | 'root') => {
    e.preventDefault();
    if (draggingDoc) setDraggingOver(target);
  };
  const onFolderDrop = (e: React.DragEvent, target: number | 'root') => {
    e.preventDefault();
    if (draggingDoc)
      moveDocument(draggingDoc, target === 'root' ? null : target);
    setDraggingDoc(null);
    setDraggingOver(null);
  };

  const displayDocs = selectedFolder
    ? documents.filter((d) => d.folder_id === selectedFolder.id)
    : documents;

  // Rubber band rect in screen coords for rendering
  const getRubberBandStyle = () => {
    if (!rubberBand || !listRef.current) return {};
    const rect = listRef.current.getBoundingClientRect();
    const scroll = listRef.current.scrollTop;
    const x1 = Math.min(rubberBand.startX, rubberBand.curX);
    const y1 = Math.min(rubberBand.startY, rubberBand.curY) - scroll;
    const w = Math.abs(rubberBand.curX - rubberBand.startX);
    const h = Math.abs(rubberBand.curY - rubberBand.startY);
    return { left: rect.left + x1, top: rect.top + y1, width: w, height: h };
  };

  return (
    <div className="flex h-screen bg-white dark:bg-[#212121] text-gray-900 dark:text-white relative">
      {/* Rubber band selection rectangle */}
      {rubberBand && (
        <div
          className="fixed z-40 border border-blue-400 bg-blue-400/10 pointer-events-none"
          style={getRubberBandStyle()}
        />
      )}

      {/* Left sidebar */}
      <aside
        className={`${sidebarOpen ? 'w-64' : 'w-14'} transition-all duration-200 overflow-hidden flex-shrink-0 bg-[#F7F7F8] dark:bg-[#171717] flex flex-col border-r border-gray-200 dark:border-gray-700`}
      >
        <div className={`p-3 flex items-center gap-2 ${sidebarOpen ? '' : 'justify-center'}`}>
          <RocketLogo className="w-7 h-7 flex-shrink-0" />
          {sidebarOpen && <span className="font-semibold text-sm truncate">Anote AI</span>}
        </div>
        <div className="px-2 pb-1 space-y-0.5">
          <button
            onClick={() => nav('/app')}
            title="Chat"
            className={`w-full rounded-lg text-sm hover:bg-gray-200 dark:hover:bg-[#2F2F2F] transition-colors flex items-center gap-2 ${
              sidebarOpen ? 'text-left px-3 py-2' : 'justify-center py-2'
            }`}
          >
            <svg
              className="w-4 h-4 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.86 9.86 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            {sidebarOpen && 'Chat'}
          </button>
          <button
            onClick={() => nav('/documents')}
            title="Library"
            className={`w-full rounded-lg text-sm bg-gray-200 dark:bg-[#2F2F2F] flex items-center gap-2 ${
              sidebarOpen ? 'text-left px-3 py-2' : 'justify-center py-2'
            }`}
          >
            <svg
              className="w-4 h-4 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V7z"
              />
            </svg>
            {sidebarOpen && 'Library'}
          </button>
        </div>
        {!sidebarOpen && <div className="flex-1" />}
        {sidebarOpen && (
        <>
        <div className="px-3 pt-3 pb-1">
          <p className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
            My Documents
          </p>
        </div>
        <div className="px-2">
          <div
            onClick={() => setSelectedFolder(null)}
            onDragOver={(e) => onFolderDragOver(e, 'root')}
            onDrop={(e) => onFolderDrop(e, 'root')}
            className={`flex items-center justify-between px-3 py-2 rounded-lg text-sm cursor-pointer transition-colors ${selectedFolder === null ? 'bg-gray-200 dark:bg-[#2F2F2F]' : 'hover:bg-gray-200 dark:hover:bg-[#2F2F2F]'} ${draggingOver === 'root' ? 'ring-2 ring-gray-400' : ''}`}
          >
            <span className="flex items-center gap-2">
              <svg
                className="w-4 h-4 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <span>All documents</span>
            </span>
            <span className="text-xs text-gray-400">{documents.length}</span>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto px-2 pt-1 space-y-0.5">
          {folders.map((folder) => (
            <div
              key={folder.id}
              onDragOver={(e) => onFolderDragOver(e, folder.id)}
              onDrop={(e) => onFolderDrop(e, folder.id)}
              className={`group flex items-center justify-between px-3 py-2 rounded-lg text-sm cursor-pointer transition-colors ${selectedFolder?.id === folder.id ? 'bg-gray-200 dark:bg-[#2F2F2F]' : 'hover:bg-gray-200 dark:hover:bg-[#2F2F2F]'} ${draggingOver === folder.id ? 'ring-2 ring-gray-400' : ''}`}
              onClick={() => setSelectedFolder(folder)}
            >
              {renamingId === folder.id ? (
                <input
                  autoFocus
                  value={renameValue}
                  onChange={(e) => setRenameValue(e.target.value)}
                  onBlur={() => renameFolder(folder.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') renameFolder(folder.id);
                    if (e.key === 'Escape') setRenamingId(null);
                  }}
                  onClick={(e) => e.stopPropagation()}
                  className="flex-1 bg-white dark:bg-[#1a1a1a] border border-gray-300 dark:border-gray-600 rounded px-1 text-sm focus:outline-none"
                />
              ) : (
                <span className="flex items-center gap-2 truncate">
                  <svg
                    className="w-4 h-4 flex-shrink-0"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M3 7a2 2 0 012-2h4l2 2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V7z"
                    />
                  </svg>
                  <span className="truncate">{folder.name}</span>
                </span>
              )}
              <div className="opacity-0 group-hover:opacity-100 flex gap-1 flex-shrink-0 ml-1">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setRenamingId(folder.id);
                    setRenameValue(folder.name);
                  }}
                  className="text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 p-0.5"
                  title="Rename"
                >
                  <svg
                    className="w-3.5 h-3.5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                    />
                  </svg>
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteFolder(folder.id);
                  }}
                  className="text-gray-400 hover:text-red-500 p-0.5"
                  title="Delete"
                >
                  <svg
                    className="w-3.5 h-3.5"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>
          ))}
          {creatingFolder ? (
            <div className="px-3 py-1">
              <input
                autoFocus
                value={newFolderName}
                onChange={(e) => setNewFolderName(e.target.value)}
                onBlur={() => {
                  if (!newFolderName.trim()) setCreatingFolder(false);
                  else createFolder();
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') createFolder();
                  if (e.key === 'Escape') setCreatingFolder(false);
                }}
                placeholder="Folder name..."
                className="w-full bg-white dark:bg-[#1a1a1a] border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm focus:outline-none"
              />
            </div>
          ) : (
            <button
              onClick={() => setCreatingFolder(true)}
              className="w-full text-left px-3 py-2 rounded-lg text-sm text-gray-400 dark:text-gray-500 hover:bg-gray-200 dark:hover:bg-[#2F2F2F] transition-colors flex items-center gap-2"
            >
              <svg
                className="w-4 h-4 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 4v16m8-8H4"
                />
              </svg>
              New folder
            </button>
          )}
        </div>
        </>
        )}
        <UserMenu sidebarOpen={sidebarOpen} />
      </aside>

      {/* Main panel */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="flex items-center justify-between px-4 py-3 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen((o) => !o)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-[#2F2F2F] text-gray-500 dark:text-gray-400"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
            </button>
            <nav className="flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400">
              <button
                onClick={() => setSelectedFolder(null)}
                className="hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                My Documents
              </button>
              {selectedFolder && (
                <>
                  <span>/</span>
                  <span className="text-gray-900 dark:text-white font-medium">
                    {selectedFolder.name}
                  </span>
                </>
              )}
            </nav>
          </div>
        </header>

        {/* Bulk action toolbar */}
        {selectedDocs.size > 0 && (
          <div className="flex items-center gap-3 px-6 py-2 bg-blue-50 dark:bg-blue-950/40 border-b border-blue-200 dark:border-blue-800">
            <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
              {selectedDocs.size} selected
            </span>
            <div className="flex items-center gap-1">
              <select
                value={bulkMoveFolder}
                onChange={(e) => setBulkMoveFolder(e.target.value)}
                className="text-xs bg-white dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-600 rounded px-2 py-1 focus:outline-none"
              >
                <option value="">Move to...</option>
                <option value="root">Unfiled</option>
                {folders.map((f) => (
                  <option key={f.id} value={String(f.id)}>
                    {f.name}
                  </option>
                ))}
              </select>
              {bulkMoveFolder && (
                <button
                  onClick={() =>
                    moveSelected(
                      bulkMoveFolder === 'root'
                        ? null
                        : parseInt(bulkMoveFolder),
                    )
                  }
                  className="text-xs px-2 py-1 rounded bg-blue-600 text-white hover:bg-blue-700 transition-colors"
                >
                  Move
                </button>
              )}
            </div>
            <button
              onClick={deleteSelected}
              className="text-xs px-2 py-1 rounded text-red-600 hover:bg-red-50 dark:hover:bg-red-950/30 transition-colors"
            >
              Delete selected
            </button>
            <button
              onClick={() => setSelectedDocs(new Set())}
              className="ml-auto text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              Clear selection
            </button>
          </div>
        )}

        {/* Document list */}
        <div
          ref={listRef}
          className="flex-1 overflow-y-auto px-6 py-4 select-none"
          onMouseDown={onListMouseDown}
        >
          {displayDocs.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
              <svg
                className="w-16 h-16 text-gray-200 dark:text-gray-700"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <p className="text-gray-400 dark:text-gray-500">
                No documents yet
              </p>
              <p className="text-xs text-gray-300 dark:text-gray-600">
                Upload files from a chat to use them as context — they'll show up here too
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
              {displayDocs.map((doc) => {
                const isSelected = selectedDocs.has(doc.id);
                return (
                  <div
                    key={doc.id}
                    data-doc-item="true"
                    ref={(el) => {
                      if (el) docItemRefs.current.set(doc.id, el);
                      else docItemRefs.current.delete(doc.id);
                    }}
                    draggable
                    onDragStart={() => onDocDragStart(doc.id)}
                    onDragEnd={onDocDragEnd}
                    onClick={(e) => onDocClick(e, doc.id, displayDocs)}
                    onMouseDown={(e) => e.stopPropagation()}
                    className={`group relative flex flex-col rounded-xl p-2 transition-colors cursor-pointer ${
                      isSelected
                        ? 'bg-blue-100 dark:bg-blue-900/40 ring-2 ring-blue-400 dark:ring-blue-500'
                        : 'bg-[#F7F7F8] dark:bg-[#2F2F2F] hover:bg-gray-100 dark:hover:bg-[#3a3a3a]'
                    }`}
                  >
                    <div
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedDocs((prev) => {
                          const next = new Set(prev);
                          next.has(doc.id) ? next.delete(doc.id) : next.add(doc.id);
                          return next;
                        });
                        setLastClickedId(doc.id);
                      }}
                      className={`absolute top-3 left-3 z-10 w-5 h-5 rounded border flex items-center justify-center cursor-pointer transition-opacity ${
                        isSelected
                          ? 'opacity-100 bg-blue-500 border-blue-500'
                          : 'opacity-0 group-hover:opacity-100 bg-white/90 dark:bg-black/50 border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                      }`}
                    >
                      {isSelected && (
                        <svg
                          className="w-3 h-3 text-white"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={3}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      )}
                    </div>
                    <div className="absolute top-3 right-3 z-10 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setViewingDoc(doc);
                        }}
                        className="w-6 h-6 rounded-full bg-white/90 dark:bg-black/50 flex items-center justify-center text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                        title="View file"
                      >
                        <svg
                          className="w-3.5 h-3.5"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                          />
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                          />
                        </svg>
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteDocument(doc.id);
                        }}
                        className="w-6 h-6 rounded-full bg-white/90 dark:bg-black/50 flex items-center justify-center text-gray-600 dark:text-gray-300 hover:text-red-500"
                        title="Delete"
                      >
                        <svg
                          className="w-3 h-3"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M6 18L18 6M6 6l12 12"
                          />
                        </svg>
                      </button>
                    </div>
                    <div className="aspect-[3/4] w-full rounded-lg overflow-hidden">
                      <DocThumbnail docId={doc.id} token={token} size="lg" />
                    </div>
                    <p
                      className="text-xs font-medium truncate mt-2 px-0.5"
                      title={doc.filename}
                    >
                      {doc.filename}
                    </p>
                    <p className="text-[10px] text-gray-400 dark:text-gray-500 px-0.5 mt-0.5">
                      {doc.chunks} chunks
                    </p>
                    {doc.chat_id && (
                      <span
                        className="mt-1 mx-0.5 inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-300 truncate text-[10px]"
                        title={`Attached to chat: ${doc.chat_name || 'Untitled chat'}`}
                      >
                        <svg
                          className="w-3 h-3 flex-shrink-0"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.86 9.86 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                          />
                        </svg>
                        <span className="truncate">{doc.chat_name || 'Untitled chat'}</span>
                      </span>
                    )}
                    <select
                      value={doc.folder_id ?? ''}
                      onChange={(e) => {
                        e.stopPropagation();
                        moveDocument(
                          doc.id,
                          e.target.value ? parseInt(e.target.value) : null,
                        );
                      }}
                      onClick={(e) => e.stopPropagation()}
                      className="mt-1 w-full text-[10px] bg-white dark:bg-[#1a1a1a] border border-gray-200 dark:border-gray-600 rounded px-1 py-0.5 focus:outline-none text-gray-600 dark:text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity"
                      title="Move to folder"
                    >
                      <option value="">Unfiled</option>
                      {folders.map((f) => (
                        <option key={f.id} value={f.id}>
                          {f.name}
                        </option>
                      ))}
                    </select>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
      <FileViewerModal
        doc={viewingDoc}
        token={token}
        onClose={() => setViewingDoc(null)}
      />
    </div>
  );
}
