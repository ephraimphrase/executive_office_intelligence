"use client";

import React from "react";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import DocumentRepository from "@/components/documents/DocumentRepository";
import { Document } from "@/lib/api";

interface DocumentsClientProps {
  documents: Document[];
}

export default function DocumentsClient({ documents }: DocumentsClientProps) {
  return (
    <>
      <Sidebar />
      <TopNav title="Executive Office" subtitle="Tier 1 Access" />
      <main className="md:ml-64 pt-20 h-screen overflow-y-auto custom-scrollbar bg-background">
        <DocumentRepository documents={documents} />
      </main>
    </>
  );
}
