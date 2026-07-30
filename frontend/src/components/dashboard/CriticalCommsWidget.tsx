import React from "react";

export interface EmailItem {
  id: string;
  sender: string;
  time: string;
  subject: string;
  isUnread: boolean;
}

interface CriticalCommsWidgetProps {
  emails: EmailItem[];
}

export default function CriticalCommsWidget({
  emails,
}: CriticalCommsWidgetProps) {
  return (
    <section className="glass-card rounded-xl p-6">
      <h2 className="font-headline-md text-headline-md text-primary flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-[24px]">
          mark_email_unread
        </span>
        Critical Comms
      </h2>

      <div className="space-y-4">
        {emails.map((email) => (
          <div
            key={email.id}
            className="p-4 bg-white border border-slate-200 rounded-lg hover:border-primary transition-colors cursor-pointer group"
          >
            <div className="flex justify-between items-start mb-1">
              <span className="font-label-sm text-label-sm text-on-surface-variant font-bold">
                {email.sender}
              </span>
              <span className="font-label-sm text-label-sm text-on-surface-variant">
                {email.time}
              </span>
            </div>
            <h4 className="font-label-md text-label-md font-semibold text-on-surface mb-2 group-hover:text-primary transition-colors">
              {email.subject}
            </h4>
            {email.isUnread && (
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-error rounded-full"></span>
                <span className="font-label-sm text-label-sm text-error">
                  UNREAD
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
