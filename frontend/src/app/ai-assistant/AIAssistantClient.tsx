"use client";

import React from "react";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import ChatContainer from "@/components/ai-assistant/ChatContainer";

export default function AIAssistantClient() {
  return (
    <>
      <Sidebar />
      <TopNav title="AI Assistant" subtitle="Session Intelligence: Optimal" />
      <main className="md:ml-64 relative h-screen flex flex-col bg-surface max-w-[1440px] mx-auto">
        <ChatContainer />
      </main>
    </>
  );
}
