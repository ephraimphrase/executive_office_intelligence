"use client";

import React, { useState, useRef } from "react";
import { Document, uploadDocument } from "@/lib/api";
import DocumentVersionModal from "./DocumentVersionModal";

interface DocumentRepositoryProps {
  documents: Document[];
}

export default function DocumentRepository({ documents: initialDocuments }: DocumentRepositoryProps) {
  const [documents, setDocuments] = useState<Document[]>(initialDocuments);
  const [isUploading, setIsUploading] = useState(false);
  const [historyDoc, setHistoryDoc] = useState<Document | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const boardPapers = documents.filter(d => d.category === "BOARD");
  const financialReports = documents.filter(d => d.category === "FINANCIAL");
  const briefingDocs = documents.filter(d => d.category === "BRIEFING");

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // For demonstration, we'll prompt for category or default to BRIEFING
    const category = prompt("Enter category (BOARD, FINANCIAL, BRIEFING):", "BRIEFING") || "GENERAL";
    const subcategory = "UPLOADED";

    try {
      setIsUploading(true);
      const newDoc = await uploadDocument(file, category, subcategory);
      setDocuments(prev => [newDoc, ...prev]);
    } catch {
      alert("Upload failed. Make sure backend is running.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const renderDocumentCard = (doc: Document) => {
    let icon = "description";
    let iconBg = "bg-surface-container";
    let iconColor = "text-on-surface-variant";
    
    if (doc.type === "PDF") {
      icon = "picture_as_pdf";
      iconBg = "bg-red-50";
      iconColor = "text-red-600";
    } else if (doc.type === "EXCEL") {
      icon = "table_chart";
      iconBg = "bg-green-50";
      iconColor = "text-green-600";
    } else if (doc.type === "WORD") {
      icon = "sticky_note_2";
      iconBg = "bg-blue-50";
      iconColor = "text-blue-600";
    }

    return (
      <div key={doc.id} className="glass-card rounded-xl p-6 flex flex-col relative group cursor-pointer hover:-translate-y-1">
        <div className={`w-12 h-12 ${iconBg} rounded-lg flex items-center justify-center ${iconColor} mb-4`}>
          <span className="material-symbols-outlined text-[32px]">{icon}</span>
        </div>
        <h4 className="font-headline-md text-[18px] text-primary mb-1 line-clamp-1">{doc.title}</h4>
        <p className="font-label-sm text-label-sm text-on-surface-variant/60 mb-8 uppercase tracking-wider">
          Modified {new Date(doc.last_modified).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
        </p>
        <div className="mt-auto flex justify-between items-center">
          <span className="font-label-sm text-label-sm px-2 py-1 bg-surface-container rounded text-on-surface-variant">
            {doc.access_level}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setHistoryDoc(doc);
              }}
              className="w-9 h-9 flex items-center justify-center rounded-lg border border-outline-variant/20 text-on-surface-variant hover:text-primary hover:border-primary/40 transition-colors"
              title="Version history"
            >
              <span className="material-symbols-outlined text-[18px]">history</span>
            </button>
            <button className="bg-primary text-on-primary px-4 py-2 rounded-lg font-label-sm text-label-sm flex items-center gap-2 shadow-lg">
              <span className="material-symbols-outlined text-[14px]">auto_awesome</span>
              Summarize
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-[1440px] mx-auto px-12 py-10 w-full">
      {/* Page Header */}
      <div className="flex justify-between items-end mb-12">
        <div>
          <h2 className="font-headline-lg text-headline-lg text-primary">Intelligence Repository</h2>
          <p className="font-body-md text-body-md text-on-surface-variant max-w-xl mt-2">
            Secure access to executive briefing papers, financial audits, and strategic board materials.
          </p>
        </div>
        <div className="flex gap-4">
          <button className="px-6 py-3 border border-outline-variant text-primary font-label-md text-label-md rounded-lg hover:bg-surface-container-low transition-all">
            Filter By Date
          </button>
          
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            className="hidden" 
          />
          <button 
            onClick={handleUploadClick}
            disabled={isUploading}
            className={`px-6 py-3 ${isUploading ? 'bg-primary/70' : 'bg-primary'} text-on-primary font-label-md text-label-md rounded-lg flex items-center gap-2 hover:bg-primary/90 transition-all`}
          >
            <span className="material-symbols-outlined text-[18px]">
              {isUploading ? "hourglass_empty" : "upload_file"}
            </span>
            {isUploading ? "Uploading..." : "Upload New"}
          </button>
        </div>
      </div>

      {/* Recent Board Papers */}
      {boardPapers.length > 0 && (
        <section className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-headline-md text-headline-md text-primary flex items-center gap-3">
              <span className="w-2 h-8 bg-primary rounded-full"></span>
              Recent Board Papers
            </h3>
            <button className="text-secondary font-label-md text-label-md hover:underline">
              View Archive
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {boardPapers.map(renderDocumentCard)}
          </div>
        </section>
      )}

      {/* Financial Reports */}
      {financialReports.length > 0 && (
        <section className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-headline-md text-headline-md text-primary flex items-center gap-3">
              <span className="w-2 h-8 bg-secondary rounded-full"></span>
              Financial Reports
            </h3>
            <button className="text-secondary font-label-md text-label-md hover:underline">
              Full Ledger Access
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {financialReports.map(renderDocumentCard)}
          </div>
        </section>
      )}

      {/* Briefing Documents */}
      {briefingDocs.length > 0 && (
        <section className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h3 className="font-headline-md text-headline-md text-primary flex items-center gap-3">
              <span className="w-2 h-8 bg-outline rounded-full"></span>
              Briefing Documents
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {briefingDocs.map(renderDocumentCard)}
          </div>
        </section>
      )}

      {/* Floating Action Button for AI */}
      <button className="fixed bottom-10 right-10 w-16 h-16 bg-primary text-on-primary rounded-full shadow-2xl flex items-center justify-center hover:scale-110 transition-transform z-50">
        <span className="material-symbols-outlined text-[28px]">smart_toy</span>
      </button>

      {historyDoc && (
        <DocumentVersionModal document={historyDoc} onClose={() => setHistoryDoc(null)} />
      )}
    </div>
  );
}
