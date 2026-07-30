"use client";

import React, { useEffect, useRef, useState } from "react";
import {
  Document,
  DocumentVersion,
  fetchDocumentVersions,
  getDocumentVersionDownloadUrl,
  uploadDocumentVersion,
} from "@/lib/api";

interface DocumentVersionModalProps {
  document: Document;
  onClose: () => void;
}

function formatBytes(bytes: number | null): string {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function DocumentVersionModal({ document, onClose }: DocumentVersionModalProps) {
  const [versions, setVersions] = useState<DocumentVersion[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let cancelled = false;
    fetchDocumentVersions(document.id).then((result) => {
      if (!cancelled) {
        setVersions(result);
        setLoaded(true);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [document.id]);

  const handleUploadNewVersion = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const changeNote = prompt("What changed in this revision? (optional)") || undefined;

    try {
      setIsUploading(true);
      const newVersion = await uploadDocumentVersion(document.id, file, changeNote);
      setVersions((prev) => [newVersion, ...prev]);
    } catch {
      alert("Failed to upload new version. Ensure backend is running.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-6" onClick={onClose}>
      <div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[80vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-start p-6 border-b border-outline-variant/10">
          <div>
            <h3 className="font-headline-md text-headline-md text-primary">Version History</h3>
            <p className="font-label-sm text-on-surface-variant mt-1">{document.title}</p>
          </div>
          <button onClick={onClose} className="text-on-surface-variant hover:text-primary">
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-3">
          {!loaded ? (
            <p className="font-label-sm text-on-surface-variant">Loading…</p>
          ) : versions.length === 0 ? (
            <p className="font-label-sm text-on-surface-variant">
              No revision history yet — this is the original upload.
            </p>
          ) : (
            versions.map((v) => (
              <a
                key={v.id}
                href={getDocumentVersionDownloadUrl(document.id, v.id)}
                className="flex items-center gap-3 p-3 bg-surface-container-low hover:bg-surface-container border border-outline-variant/10 rounded-lg transition-colors group"
              >
                <span className="material-symbols-outlined text-on-surface-variant group-hover:text-primary">
                  history
                </span>
                <div className="flex-1 min-w-0">
                  <p className="font-label-md text-primary font-semibold">
                    Version {v.version_number} — {v.name}
                  </p>
                  <p className="font-label-sm text-on-surface-variant truncate">
                    {v.change_note || "No change note"} • {formatBytes(v.size_bytes)} •{" "}
                    {new Date(v.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" })}
                  </p>
                </div>
                <span className="material-symbols-outlined text-on-surface-variant/40">download</span>
              </a>
            ))
          )}
        </div>

        <div className="p-6 border-t border-outline-variant/10">
          <input type="file" ref={fileInputRef} onChange={handleUploadNewVersion} className="hidden" />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className={`w-full py-3 ${isUploading ? "bg-primary/70" : "bg-primary"} text-on-primary font-label-md rounded-lg flex items-center justify-center gap-2 hover:bg-primary/90 transition-all`}
          >
            <span className="material-symbols-outlined text-[18px]">
              {isUploading ? "hourglass_empty" : "upload_file"}
            </span>
            {isUploading ? "Uploading…" : "Upload New Version"}
          </button>
        </div>
      </div>
    </div>
  );
}
