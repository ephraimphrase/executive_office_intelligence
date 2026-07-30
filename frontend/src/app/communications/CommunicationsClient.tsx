"use client";

import React, { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import MessageList from "@/components/communications/MessageList";
import MessageDetail from "@/components/communications/MessageDetail";
import { Email } from "@/lib/api";

interface CommunicationsClientProps {
  emails: Email[];
}

export default function CommunicationsClient({ emails: initialEmails }: CommunicationsClientProps) {
  const [emails, setEmails] = useState<Email[]>(initialEmails);
  const [selectedEmailId, setSelectedEmailId] = useState<string | null>(
    emails.length > 0 ? emails[0].id : null
  );

  const handleEmailUpdated = (emailId: string, updates: Partial<Email>) => {
    setEmails(prev => prev.map(e => e.id === emailId ? { ...e, ...updates } : e));
  };

  const selectedEmail = emails.find(e => e.id === selectedEmailId) || null;

  return (
    <>
      <Sidebar />
      <TopNav title="Communications Hub" />
      <main className="md:ml-64 pt-20 h-screen flex overflow-hidden max-w-[1440px] mx-auto">
        <MessageList 
          emails={emails} 
          selectedEmailId={selectedEmailId} 
          onSelectEmail={setSelectedEmailId} 
        />
        <MessageDetail email={selectedEmail} onEmailUpdated={handleEmailUpdated} />
      </main>
    </>
  );
}
