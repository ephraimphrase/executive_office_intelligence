"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { sendChatMessage, ChatMessage } from "@/lib/api";

const WELCOME_MSG: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Good day. I'm EOIS Intelligence — your AI Chief of Staff. I have full context of your schedule, pipeline, and strategic priorities. How can I assist you today?",
  timestamp: new Date().toISOString(),
};

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export default function ChatContainer() {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MSG]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-resize textarea
  const resizeTextarea = useCallback(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "0";
    ta.style.height = Math.min(ta.scrollHeight, 120) + "px";
    ta.style.overflowY = ta.scrollHeight > 120 ? "auto" : "hidden";
  }, []);

  // Scroll to bottom whenever messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = useCallback(async () => {
    const text = inputValue.trim();
    if (!text || isLoading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "";
    }
    setIsLoading(true);

    try {
      const result = await sendChatMessage(text, conversationId);
      if (result.conversation_id) setConversationId(result.conversation_id);

      const aiMsg: ChatMessage = {
        id: `ai-${Date.now()}`,
        role: "assistant",
        content: result.response,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } finally {
      setIsLoading(false);
    }
  }, [inputValue, isLoading, conversationId]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <>
      {/* Chat Messages */}
      <section className="flex-1 mt-20 mb-28 overflow-y-auto px-6 md:px-12 py-10 flex flex-col gap-8 scroll-smooth custom-scrollbar">
        {/* Session marker */}
        <div className="flex justify-center mb-4">
          <div className="bg-surface-container px-4 py-1.5 rounded-full border border-outline-variant/30">
            <span className="font-label-sm text-label-sm text-on-surface-variant">
              Analytical Session Initiated • {formatTime(new Date().toISOString())}
            </span>
          </div>
        </div>

        {messages.map((msg) =>
          msg.role === "user" ? (
            // User bubble
            <div key={msg.id} className="flex flex-col items-end gap-2 max-w-2xl ml-auto">
              <div className="bg-primary text-on-primary px-6 py-4 rounded-2xl rounded-tr-none shadow-sm">
                <p className="font-body-md text-body-md whitespace-pre-wrap">{msg.content}</p>
              </div>
              <span className="font-label-sm text-label-sm text-on-surface-variant/60 mr-2">
                GVP Office • {formatTime(msg.timestamp)}
              </span>
            </div>
          ) : (
            // AI bubble
            <div key={msg.id} className="flex flex-col items-start gap-4 max-w-4xl">
              <div className="flex items-center gap-3 mb-1">
                <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-on-primary">
                  <span className="material-symbols-outlined text-base">smart_toy</span>
                </div>
                <span className="font-label-md text-label-md text-primary font-bold">
                  EOIS Intelligence
                </span>
                <span className="text-[11px] text-on-surface-variant/50">{formatTime(msg.timestamp)}</span>
              </div>
              <div className="glass-panel w-full p-6 rounded-3xl rounded-tl-none border border-outline-variant/10">
                <p className="font-body-md text-body-md leading-relaxed text-on-surface whitespace-pre-wrap">
                  {msg.content}
                </p>
              </div>
            </div>
          )
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex items-center gap-3 text-on-surface-variant/40">
            <div className="w-8 h-8 rounded-lg bg-surface-container flex items-center justify-center">
              <span className="material-symbols-outlined text-base animate-spin">progress_activity</span>
            </div>
            <div className="glass-panel px-6 py-4 rounded-3xl rounded-tl-none border border-outline-variant/10">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce [animation-delay:300ms]" />
                <span className="font-label-md text-label-md italic text-on-surface-variant ml-2">
                  Synthesizing intelligence...
                </span>
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </section>

      {/* Input Area */}
      <footer className="fixed bottom-0 right-0 left-0 md:left-64 p-6 bg-surface/80 backdrop-blur-md z-30">
        <div className="max-w-5xl mx-auto glass-panel p-2 rounded-2xl border border-outline-variant/40 shadow-xl relative">
          <div className="flex items-end gap-2">
            <button
              className="p-3 text-on-surface-variant hover:text-primary hover:bg-surface-container-high rounded-xl transition-all"
              title="Attach Document"
            >
              <span className="material-symbols-outlined">attach_file</span>
            </button>
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => {
                setInputValue(e.target.value);
                resizeTextarea();
              }}
              onKeyDown={handleKeyDown}
              className="flex-1 bg-transparent border-none focus:ring-0 py-3 text-body-md placeholder:text-on-surface-variant/50 resize-none overflow-hidden outline-none custom-scrollbar"
              placeholder="Ask about strategy, risks, reports, schedule… (⌘+Enter to send)"
              rows={1}
            />
            <div className="flex items-center gap-2 px-2">
              <button
                className="p-3 text-on-surface-variant hover:text-primary hover:bg-surface-container-high rounded-xl transition-all"
                title="Voice Command"
              >
                <span className="material-symbols-outlined">mic</span>
              </button>
              <button
                onClick={handleSend}
                disabled={isLoading || !inputValue.trim()}
                className="bg-primary text-on-primary p-3 rounded-xl hover:bg-primary/90 shadow-md active:scale-95 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                title="Send (⌘+Enter)"
              >
                <span
                  className="material-symbols-outlined"
                  style={{ fontVariationSettings: "'FILL' 1" }}
                >
                  {isLoading ? "hourglass_empty" : "send"}
                </span>
              </button>
            </div>
          </div>
          {/* Context Pill */}
          <div className="absolute -top-8 left-4">
            <div className="flex items-center gap-2 px-3 py-1 bg-primary/5 border border-primary/10 rounded-full">
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
              <span className="text-[10px] font-bold text-primary uppercase tracking-widest">
                {conversationId ? `Session: ${conversationId.slice(0, 8)}…` : "New Session"}
              </span>
            </div>
          </div>
        </div>
        <p className="text-center text-[10px] text-on-surface-variant/40 mt-3 uppercase tracking-[0.2em]">
          EOIS v4.2.1 • Enterprise Confidential • End-to-End Encrypted
        </p>
      </footer>
    </>
  );
}
