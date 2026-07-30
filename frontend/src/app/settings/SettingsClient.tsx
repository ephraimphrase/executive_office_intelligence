"use client";

import React from "react";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import SettingsManager from "@/components/settings/SettingsManager";

export default function SettingsClient() {
  return (
    <>
      <Sidebar />
      <TopNav title="Settings & Configuration" />
      <main className="md:ml-64 pt-20 h-screen overflow-y-auto px-margin-mobile md:px-margin-desktop py-12 bg-background">
        <SettingsManager />
      </main>
    </>
  );
}
