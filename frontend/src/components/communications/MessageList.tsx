"use client";

import React from "react";
import { Email } from "@/lib/api";

interface MessageListProps {
  emails: Email[];
  selectedEmailId: string | null;
  onSelectEmail: (id: string) => void;
}

export default function MessageList({ emails, selectedEmailId, onSelectEmail }: MessageListProps) {
  return (
    <section className="w-full lg:w-[440px] border-r border-outline-variant/20 flex flex-col bg-white overflow-hidden shrink-0">
      <div className="p-6 border-b border-outline-variant/10 flex justify-between items-center bg-surface-container-lowest">
        <h2 className="font-headline-md text-headline-md text-primary">Priority Inbox</h2>
        <button className="text-on-surface-variant hover:text-primary transition-colors">
          <span className="material-symbols-outlined">tune</span>
        </button>
      </div>
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {emails.map((email) => {
          const isSelected = selectedEmailId === email.id;
          const isUnread = email.status === "UNREAD";
          
          return (
            <div
              key={email.id}
              onClick={() => onSelectEmail(email.id)}
              className={`p-6 cursor-pointer transition-all border-b border-outline-variant/10 relative group ${
                isSelected ? "active-message-gradient" : "hover:bg-slate-50"
              } ${!isUnread && !isSelected ? "opacity-70" : ""}`}
            >
              {isSelected && <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary"></div>}
              
              <div className="flex justify-between items-start mb-1">
                <span className={`font-label-md text-label-md ${isUnread || isSelected ? "text-primary font-bold" : "text-on-surface-variant font-medium"}`}>
                  {email.sender_name}
                </span>
                <span className="font-label-sm text-label-sm text-on-surface-variant/70">
                  {new Date(email.received_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              
              <div className="flex items-center gap-2 mb-2">
                <span className={`material-symbols-outlined text-sm ${email.priority === 'URGENT' ? 'text-error fill-icon' : 'text-blue-600'}`}>
                  {email.priority === 'URGENT' ? 'priority_high' : 'alternate_email'}
                </span>
                <p className={`font-label-sm text-label-sm uppercase ${email.priority === 'URGENT' ? 'text-error' : 'text-blue-600'}`}>
                  {email.priority === 'URGENT' ? 'Urgent' : 'Standard'}
                </p>
              </div>
              
              <p className={`font-body-md text-body-md mb-1 truncate ${isUnread || isSelected ? "font-semibold text-on-surface" : "text-on-surface"}`}>
                {email.subject}
              </p>
              
              <p className="font-body-md text-body-md text-on-surface-variant/80 line-clamp-2">
                Click to view the full details of this communication thread.
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}
