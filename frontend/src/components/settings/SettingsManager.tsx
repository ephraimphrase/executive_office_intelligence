"use client";

import React, { useState } from "react";

type TabId = "profile" | "integrations" | "ai" | "security";

export default function SettingsManager() {
  const [activeTab, setActiveTab] = useState<TabId>("profile");
  const [analyticalDepth, setAnalyticalDepth] = useState(85);

  const getDepthLabel = (val: number) => {
    if (val < 33) return "Executive Summary";
    if (val < 66) return "Standard Analysis";
    return "High Precision Audit";
  };

  return (
    <div className="max-w-6xl mx-auto w-full">
      <div className="mb-8">
        <h3 className="font-headline-lg text-headline-lg text-primary tracking-tight">System Controls</h3>
        <p className="text-on-surface-variant font-body-md text-body-md mt-2">
          Manage your executive interface and intelligence data flow.
        </p>
      </div>

      <div className="glass-panel rounded-2xl flex min-h-[600px] overflow-hidden shadow-sm">
        {/* Vertical Sub-Navigation */}
        <nav className="w-64 border-r border-outline-variant/20 py-8 px-6 space-y-2 shrink-0">
          <button
            onClick={() => setActiveTab("profile")}
            className={`w-full text-left px-4 py-3 rounded-lg font-label-md text-label-md flex items-center transition-colors ${
              activeTab === "profile"
                ? "text-primary font-bold bg-surface-container-high"
                : "text-on-surface-variant hover:bg-surface-container-low"
            }`}
          >
            <span className="material-symbols-outlined mr-3 text-[20px]">account_circle</span>
            Profile
          </button>
          <button
            onClick={() => setActiveTab("integrations")}
            className={`w-full text-left px-4 py-3 rounded-lg font-label-md text-label-md flex items-center transition-colors ${
              activeTab === "integrations"
                ? "text-primary font-bold bg-surface-container-high"
                : "text-on-surface-variant hover:bg-surface-container-low"
            }`}
          >
            <span className="material-symbols-outlined mr-3 text-[20px]">hub</span>
            Integrations
          </button>
          <button
            onClick={() => setActiveTab("ai")}
            className={`w-full text-left px-4 py-3 rounded-lg font-label-md text-label-md flex items-center transition-colors ${
              activeTab === "ai"
                ? "text-primary font-bold bg-surface-container-high"
                : "text-on-surface-variant hover:bg-surface-container-low"
            }`}
          >
            <span className="material-symbols-outlined mr-3 text-[20px]">neurology</span>
            AI Preferences
          </button>
          <button
            onClick={() => setActiveTab("security")}
            className={`w-full text-left px-4 py-3 rounded-lg font-label-md text-label-md flex items-center transition-colors ${
              activeTab === "security"
                ? "text-primary font-bold bg-surface-container-high"
                : "text-on-surface-variant hover:bg-surface-container-low"
            }`}
          >
            <span className="material-symbols-outlined mr-3 text-[20px]">security</span>
            Security
          </button>
        </nav>

        {/* Content Area */}
        <div className="flex-1 p-10 overflow-y-auto bg-white/20">
          {/* Profile Tab */}
          {activeTab === "profile" && (
            <section className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <h4 className="font-headline-md text-headline-md mb-8">Professional Identity</h4>
              <div className="grid grid-cols-2 gap-8">
                <div className="space-y-2">
                  <label className="font-label-sm text-label-sm uppercase text-on-surface-variant">Office Name</label>
                  <input
                    className="w-full border border-outline-variant rounded-lg px-4 py-3 font-body-md text-body-md transition-all hover:border-outline focus:border-primary focus:ring-1 focus:ring-primary outline-none"
                    type="text"
                    defaultValue="GVP Office"
                  />
                </div>
                <div className="space-y-2">
                  <label className="font-label-sm text-label-sm uppercase text-on-surface-variant">Executive Title</label>
                  <input
                    className="w-full border border-outline-variant rounded-lg px-4 py-3 font-body-md text-body-md transition-all hover:border-outline focus:border-primary focus:ring-1 focus:ring-primary outline-none"
                    type="text"
                    defaultValue="Chief Strategy Officer"
                  />
                </div>
                <div className="space-y-2 col-span-2">
                  <label className="font-label-sm text-label-sm uppercase text-on-surface-variant">Contact Email</label>
                  <input
                    className="w-full border border-outline-variant rounded-lg px-4 py-3 font-body-md text-body-md transition-all hover:border-outline focus:border-primary focus:ring-1 focus:ring-primary outline-none"
                    type="email"
                    defaultValue="executive.office@eois.intelligence"
                  />
                </div>
                <div className="space-y-2 col-span-2">
                  <label className="font-label-sm text-label-sm uppercase text-on-surface-variant">Biography & Mandate</label>
                  <textarea
                    className="w-full border border-outline-variant rounded-lg px-4 py-3 font-body-md text-body-md transition-all hover:border-outline focus:border-primary focus:ring-1 focus:ring-primary outline-none resize-none"
                    rows={4}
                    defaultValue="Directing global strategic initiatives and resource allocation across three continents. Primary focus on AI-driven forecasting and operational excellence."
                  />
                </div>
              </div>
              <div className="mt-12 flex justify-end">
                <button className="bg-primary text-white px-8 py-3 rounded-lg font-bold transition-transform active:scale-95 shadow-md hover:bg-primary-container">
                  Update Profile
                </button>
              </div>
            </section>
          )}

          {/* Integrations Tab */}
          {activeTab === "integrations" && (
            <section className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <h4 className="font-headline-md text-headline-md mb-8">System Connectivity</h4>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-white/40 border border-outline-variant/20 rounded-xl transition-all hover:shadow-md">
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-lg bg-blue-50 flex items-center justify-center mr-4">
                      <span className="material-symbols-outlined text-blue-600">mail</span>
                    </div>
                    <div>
                      <p className="font-label-md text-label-md font-bold text-on-surface">Microsoft 365</p>
                      <p className="text-xs text-on-surface-variant">Sync calendar, emails, and OneDrive documents.</p>
                    </div>
                  </div>
                  <label className="switch">
                    <input type="checkbox" defaultChecked />
                    <span className="slider"></span>
                  </label>
                </div>

                <div className="flex items-center justify-between p-4 bg-white/40 border border-outline-variant/20 rounded-xl transition-all hover:shadow-md">
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-lg bg-purple-50 flex items-center justify-center mr-4">
                      <span className="material-symbols-outlined text-purple-600">forum</span>
                    </div>
                    <div>
                      <p className="font-label-md text-label-md font-bold text-on-surface">Slack Enterprise</p>
                      <p className="text-xs text-on-surface-variant">Automated briefing distribution to leadership channels.</p>
                    </div>
                  </div>
                  <label className="switch">
                    <input type="checkbox" defaultChecked />
                    <span className="slider"></span>
                  </label>
                </div>

                <div className="flex items-center justify-between p-4 bg-white/40 border border-outline-variant/20 rounded-xl transition-all hover:shadow-md">
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-lg bg-sky-50 flex items-center justify-center mr-4">
                      <span className="material-symbols-outlined text-sky-600">monitoring</span>
                    </div>
                    <div>
                      <p className="font-label-md text-label-md font-bold text-on-surface">Salesforce CRM</p>
                      <p className="text-xs text-on-surface-variant">Real-time pipeline analysis and forecasting.</p>
                    </div>
                  </div>
                  <label className="switch">
                    <input type="checkbox" />
                    <span className="slider"></span>
                  </label>
                </div>

                <div className="flex items-center justify-between p-4 bg-white/40 border border-outline-variant/20 rounded-xl transition-all hover:shadow-md">
                  <div className="flex items-center">
                    <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center mr-4">
                      <span className="material-symbols-outlined text-gray-700">account_balance</span>
                    </div>
                    <div>
                      <p className="font-label-md text-label-md font-bold text-on-surface">SAP ERP</p>
                      <p className="text-xs text-on-surface-variant">Direct integration with financial and operational data.</p>
                    </div>
                  </div>
                  <label className="switch">
                    <input type="checkbox" defaultChecked />
                    <span className="slider"></span>
                  </label>
                </div>
              </div>
            </section>
          )}

          {/* AI Preferences Tab */}
          {activeTab === "ai" && (
            <section className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <h4 className="font-headline-md text-headline-md mb-8">Intelligence Synthesis</h4>
              <div className="space-y-12">
                <div className="space-y-6">
                  <div className="flex justify-between items-end">
                    <label className="font-label-sm text-label-sm uppercase text-on-surface-variant">Analytical Depth</label>
                    <span className="text-xs font-bold text-primary">{getDepthLabel(analyticalDepth)}</span>
                  </div>
                  <input
                    className="w-full h-1 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-primary transition-all"
                    max="100"
                    min="1"
                    type="range"
                    value={analyticalDepth}
                    onChange={(e) => setAnalyticalDepth(Number(e.target.value))}
                  />
                  <div className="flex justify-between text-[10px] text-on-surface-variant font-bold uppercase tracking-widest">
                    <span>Executive Summary</span>
                    <span>Comprehensive Audit</span>
                  </div>
                </div>
                <div className="p-6 bg-primary/5 rounded-2xl border border-primary/10">
                  <div className="flex items-center justify-between">
                    <div className="max-w-md">
                      <p className="font-label-md text-label-md font-bold text-primary">Proactive Insights</p>
                      <p className="text-sm text-on-surface-variant mt-1">Allow the AI to surface critical anomalies before they appear in scheduled reports.</p>
                    </div>
                    <label className="switch">
                      <input type="checkbox" defaultChecked />
                      <span className="slider"></span>
                    </label>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-6">
                  <div className="p-4 border border-outline-variant/30 rounded-xl hover:bg-white transition-colors cursor-pointer group">
                    <p className="font-label-sm text-label-sm font-bold text-primary mb-2">Primary Logic Model</p>
                    <select className="w-full border-none bg-transparent p-0 font-body-md text-body-md text-on-secondary-container focus:ring-0 outline-none cursor-pointer">
                      <option>Strategic-Reasoning-v4</option>
                      <option>Quantitative-Forecaster-Pro</option>
                      <option>Legal-Compliance-Engine</option>
                    </select>
                  </div>
                  <div className="p-4 border border-outline-variant/30 rounded-xl hover:bg-white transition-colors cursor-pointer group">
                    <p className="font-label-sm text-label-sm font-bold text-primary mb-2">Response Tone</p>
                    <select className="w-full border-none bg-transparent p-0 font-body-md text-body-md text-on-secondary-container focus:ring-0 outline-none cursor-pointer">
                      <option>Brief & Direct</option>
                      <option>Analytical & Explanatory</option>
                      <option>Colloquial Professional</option>
                    </select>
                  </div>
                </div>
              </div>
            </section>
          )}

          {/* Security Tab */}
          {activeTab === "security" && (
            <section className="animate-in fade-in slide-in-from-bottom-2 duration-300">
              <h4 className="font-headline-md text-headline-md mb-8">Access & Governance</h4>
              <div className="flex flex-col items-center justify-center py-20 text-center space-y-4">
                <span className="material-symbols-outlined text-6xl text-outline-variant">lock</span>
                <p className="text-on-surface-variant font-body-md text-body-md max-w-xs">
                  Security protocols are managed by the System Administrator. Multi-factor authentication is currently active.
                </p>
                <button className="text-primary font-bold font-label-md text-label-md border-b border-primary hover:text-on-secondary-container hover:border-on-secondary-container transition-all">
                  View Audit Logs
                </button>
              </div>
            </section>
          )}
        </div>
      </div>

      {/* Footer Meta */}
      <div className="mt-12 flex justify-between items-center text-[10px] uppercase tracking-widest text-on-surface-variant font-bold opacity-60">
        <span>EOIS v2.4.1-BUILD</span>
        <span>System Health: Optimal</span>
        <span>Last Sync: 04:12 GMT</span>
      </div>
    </div>
  );
}
