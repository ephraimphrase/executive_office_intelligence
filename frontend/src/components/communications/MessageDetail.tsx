"use client";

import React, { useState } from "react";
import { Email, sendEmailReply, updateEmailStatus } from "@/lib/api";

interface MessageDetailProps {
  email: Email | null;
  onEmailUpdated?: (emailId: string, updates: Partial<Email>) => void;
}

export default function MessageDetail({ email, onEmailUpdated }: MessageDetailProps) {
  const [replyBody, setReplyBody] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [toast, setToast] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const showToast = (type: "success" | "error", text: string) => {
    setToast({ type, text });
    setTimeout(() => setToast(null), 4000);
  };

  const handleSendReply = async () => {
    if (!email || !replyBody.trim()) return;
    setIsSending(true);
    try {
      const result = await sendEmailReply(email.id, replyBody);
      if (result.success) {
        showToast("success", "Reply sent successfully.");
        setReplyBody("");
        await updateEmailStatus(email.id, "REPLIED");
        if (onEmailUpdated) onEmailUpdated(email.id, { status: "REPLIED" });
      } else {
        showToast("error", result.message);
      }
    } catch {
      showToast("error", "Unexpected error sending reply.");
    } finally {
      setIsSending(false);
    }
  };

  const handleUpdateStatus = async (status: "READ" | "UNREAD" | "ARCHIVED" | "REPLIED") => {
    if (!email) return;
    try {
      await updateEmailStatus(email.id, status);
      if (onEmailUpdated) onEmailUpdated(email.id, { status });
      showToast("success", `Marked as ${status.toLowerCase()}.`);
    } catch {
      showToast("error", "Failed to update status.");
    }
  };

  if (!email) {
    return (
      <section className="flex-1 flex flex-col bg-surface-container-low items-center justify-center">
        <span className="material-symbols-outlined text-[64px] text-on-surface-variant/30 mb-4">
          forum
        </span>
        <p className="font-label-md text-on-surface-variant text-center">
          Select a message to view details
        </p>
      </section>
    );
  }

  return (
    <section className="flex-1 flex flex-col bg-surface-container-low overflow-hidden relative">
      {/* Toast notification */}
      {toast && (
        <div
          className={`absolute top-4 right-4 z-50 px-5 py-3 rounded-xl shadow-lg font-label-md text-sm flex items-center gap-2 transition-all ${
            toast.type === "success"
              ? "bg-green-50 text-green-800 border border-green-200"
              : "bg-error-container text-on-error-container border border-error/20"
          }`}
        >
          <span className="material-symbols-outlined text-[18px]">
            {toast.type === "success" ? "check_circle" : "error"}
          </span>
          {toast.text}
        </div>
      )}
      {/* Contextual Header Actions */}
      <div className="h-16 px-8 flex items-center justify-between bg-white border-b border-outline-variant/10 z-10 shrink-0">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => handleUpdateStatus("ARCHIVED")}
            className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-slate-100 transition-colors"
            title="Archive"
          >
            <span className="material-symbols-outlined text-xl">archive</span>
          </button>
          <button className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-slate-100 transition-colors">
            <span className="material-symbols-outlined text-xl">report</span>
          </button>
          <button className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-slate-100 transition-colors text-error">
            <span className="material-symbols-outlined text-xl">delete</span>
          </button>
        </div>
        <div className="flex items-center gap-3">
          {email.status === "READ" || email.status === "REPLIED" ? (
            <button 
              onClick={() => handleUpdateStatus("UNREAD")}
              className="px-4 py-1.5 border border-outline rounded-full font-label-sm text-label-sm hover:bg-slate-50 transition-all"
            >
              Mark Unread
            </button>
          ) : (
            <button 
              onClick={() => handleUpdateStatus("READ")}
              className="px-4 py-1.5 border border-outline rounded-full font-label-sm text-label-sm hover:bg-slate-50 transition-all"
            >
              Mark Read
            </button>
          )}
          <button 
            onClick={() => {
              const el = document.getElementById("reply-textarea");
              if (el) el.focus();
            }}
            className="px-4 py-1.5 bg-primary text-on-primary rounded-full font-label-sm text-label-sm hover:bg-primary/90 transition-all flex items-center gap-2"
          >
            <span className="material-symbols-outlined text-sm">reply</span>
            Compose Reply
          </button>
        </div>
      </div>

      {/* Detail Scroll Area */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-6 md:p-10 space-y-8 relative z-10">
        
        {/* AI Summary Box (Glassmorphic) */}
        <div className="glass-panel rounded-2xl p-6 relative overflow-hidden group bg-white/50">
          <div className="absolute top-0 right-0 p-4">
            <div className="flex items-center gap-1.5 px-3 py-1 bg-primary text-on-primary rounded-full shadow-lg scale-90 group-hover:scale-100 transition-transform">
              <span className="material-symbols-outlined text-sm animate-pulse">auto_awesome</span>
              <span className="text-[10px] font-bold uppercase tracking-widest">AI Intelligence</span>
            </div>
          </div>
          <h3 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mb-4">
            Executive Summary
          </h3>
          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="w-1 h-12 bg-primary rounded-full mt-1"></div>
              <div>
                <p className="font-body-md text-body-md text-on-surface font-semibold">{email.subject}</p>
                <p className="font-body-md text-body-md text-on-surface-variant">
                  This communication from {email.sender_name} requires your attention regarding the recent updates.
                </p>
              </div>
            </div>
            {email.priority === "URGENT" && (
              <div className="flex gap-4">
                <div className="w-1 h-12 bg-error rounded-full mt-1"></div>
                <div>
                  <p className="font-body-md text-body-md text-on-surface font-semibold text-error">Action Required</p>
                  <p className="font-body-md text-body-md text-on-surface-variant">
                    Review and provide final sign-off by EOD today.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Thread Section */}
        <div className="space-y-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="h-[1px] flex-1 bg-outline-variant/30"></div>
            <span className="font-label-sm text-label-sm text-on-surface-variant/50">
              {new Date(email.received_at).toLocaleDateString()}
            </span>
            <div className="h-[1px] flex-1 bg-outline-variant/30"></div>
          </div>

          {/* Message Bubble: External */}
          <div className="flex gap-4 items-start max-w-3xl">
            <div className="w-10 h-10 rounded-full bg-primary-fixed flex items-center justify-center flex-shrink-0">
              <span className="font-bold text-on-primary-fixed">{email.sender_name.substring(0, 2).toUpperCase()}</span>
            </div>
            <div className="bg-white p-6 rounded-2xl rounded-tl-none border border-outline-variant/10 shadow-sm space-y-4">
              <div className="flex justify-between items-center">
                <span className="font-label-md text-label-md text-primary font-bold">{email.sender_name}</span>
                <span className="font-label-sm text-label-sm text-on-surface-variant/50">
                  {new Date(email.received_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
              <div className="font-body-md text-body-md text-on-surface space-y-4 leading-relaxed">
                <p>Dear GVP,</p>
                <p>Please review the details regarding: <strong>{email.subject}</strong></p>
                <p>
                  This is a system-generated mockup message payload mirroring the schema required by the backend.
                  In production, this would render the actual HTML or plain text body of the email.
                </p>
                <p>Best Regards,<br/>{email.sender_name}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Reply Area */}
        <div className="pt-8">
          <div className="bg-white border border-outline-variant/20 rounded-2xl shadow-sm overflow-hidden focus-within:ring-1 focus-within:ring-primary/20 transition-all">
            <div className="flex items-center gap-2 px-4 py-2 bg-surface-container-lowest border-b border-outline-variant/10">
              <button className="p-1 hover:text-primary text-on-surface-variant"><span className="material-symbols-outlined text-lg">format_bold</span></button>
              <button className="p-1 hover:text-primary text-on-surface-variant"><span className="material-symbols-outlined text-lg">format_italic</span></button>
              <button className="p-1 hover:text-primary text-on-surface-variant"><span className="material-symbols-outlined text-lg">link</span></button>
              <div className="w-[1px] h-4 bg-outline-variant/30 mx-2"></div>
              <button className="p-1 hover:text-primary text-on-surface-variant"><span className="material-symbols-outlined text-lg">attach_file</span></button>
              <button className="p-1 hover:text-primary text-on-surface-variant"><span className="material-symbols-outlined text-lg">image</span></button>
            </div>
            <textarea
              id="reply-textarea"
              className="w-full p-4 border-none focus:ring-0 text-body-md placeholder:text-on-surface-variant/30 outline-none resize-none"
              placeholder="Type your executive response or use /AI to draft..."
              rows={4}
              value={replyBody}
              onChange={(e) => setReplyBody(e.target.value)}
              onKeyDown={(e) => {
                if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
                  e.preventDefault();
                  handleSendReply();
                }
              }}
            ></textarea>
            <div className="flex justify-between items-center p-4 bg-surface-container-lowest border-t border-outline-variant/10">
              <div className="flex items-center gap-4 text-on-surface-variant/40">
                <span className="font-label-sm text-label-sm">⌘ + Enter to send</span>
              </div>
              <button
                onClick={handleSendReply}
                disabled={isSending || !replyBody.trim()}
                className="px-6 py-2 bg-primary text-on-primary rounded-xl font-label-md text-label-md flex items-center gap-2 hover:bg-primary/90 transition-all active:scale-95 shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span className="material-symbols-outlined text-sm">
                  {isSending ? "hourglass_empty" : "send"}
                </span>
                {isSending ? "Sending..." : "Send Response"}
              </button>
            </div>
          </div>
        </div>
      </div>
      
      {/* Subtle Backdrop Effect */}
      <div className="absolute bottom-0 right-0 w-full h-64 pointer-events-none opacity-20 bg-gradient-to-t from-primary/5 to-transparent z-0"></div>
    </section>
  );
}
