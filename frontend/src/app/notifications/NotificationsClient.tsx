"use client";

import React from "react";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import NotificationsList from "@/components/notifications/NotificationsList";

export default function NotificationsClient() {
  return (
    <>
      <Sidebar />
      <TopNav title="Intelligence Alerts" subtitle="High-priority system notifications requiring executive review." />
      <main className="md:ml-64 pt-24 h-screen overflow-y-auto px-margin-mobile md:px-margin-desktop pb-margin-desktop bg-background">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-10 border-b border-outline-variant/20 pb-6 max-w-container-max mx-auto w-full">
          <div>
            <h1 className="font-headline-lg text-headline-lg-mobile md:text-headline-lg text-primary tracking-tight">Intelligence Alerts</h1>
            <p className="font-body-md text-body-md text-on-surface-variant mt-2 max-w-2xl">High-priority system notifications requiring executive review.</p>
          </div>
          <button className="mt-4 sm:mt-0 flex items-center space-x-2 text-on-surface-variant hover:text-primary font-label-md text-label-md px-4 py-2 rounded border border-outline-variant/30 hover:bg-surface-variant/50 transition-colors">
            <span className="material-symbols-outlined text-[20px]">done_all</span>
            <span>Mark All as Read</span>
          </button>
        </div>
        
        <NotificationsList />
      </main>
    </>
  );
}
