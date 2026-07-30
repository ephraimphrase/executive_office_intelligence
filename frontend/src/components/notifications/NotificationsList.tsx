"use client";

import React from "react";

export default function NotificationsList() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 max-w-container-max mx-auto">
      {/* Feed Column */}
      <div className="lg:col-span-8 space-y-6">
        
        {/* Critical Alerts Section */}
        <section className="animate-in fade-in slide-in-from-bottom-2 duration-300">
          <h2 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mb-4 flex items-center">
            <span className="w-2 h-2 rounded-full bg-error mr-2"></span> Critical Alerts
          </h2>
          <div className="glass-card rounded-xl p-6 cursor-pointer relative overflow-hidden group">
            {/* Subtle left border accent */}
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-error opacity-80"></div>
            
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4">
                <div className="p-2 bg-error-container/30 rounded-lg text-error mt-1">
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>warning</span>
                </div>
                <div>
                  <div className="flex items-center space-x-3 mb-1">
                    <h3 className="font-headline-md text-[18px] leading-tight text-primary">Budget variance detected in Q3 OPEX</h3>
                    <span className="px-2 py-0.5 rounded-full bg-error-container text-on-error-container font-label-sm text-[10px] uppercase">Finance</span>
                  </div>
                  <p className="font-body-md text-on-surface-variant">12% deviation found in Singapore Data Center spend against projected strategic allocation.</p>
                  <div className="flex items-center space-x-4 mt-3 text-on-surface-variant/60 font-label-sm text-[11px]">
                    <span className="flex items-center"><span className="material-symbols-outlined text-[14px] mr-1">schedule</span> 14 mins ago</span>
                    <span className="flex items-center"><span className="material-symbols-outlined text-[14px] mr-1">analytics</span> Impact: High</span>
                  </div>
                </div>
              </div>
              <span className="material-symbols-outlined text-outline-variant group-hover:text-primary transition-colors">arrow_forward</span>
            </div>
          </div>
        </section>

        {/* Action Required Section */}
        <section className="pt-2 animate-in fade-in slide-in-from-bottom-2 duration-300 delay-75">
          <h2 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mb-4 flex items-center">
            <span className="w-2 h-2 rounded-full bg-secondary mr-2"></span> Action Required
          </h2>
          
          <div className="glass-card rounded-xl p-6 cursor-pointer relative overflow-hidden group">
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-secondary opacity-80"></div>
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4">
                <div className="p-2 bg-secondary-container/30 rounded-lg text-secondary mt-1">
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>edit_document</span>
                </div>
                <div>
                  <div className="flex items-center space-x-3 mb-1">
                    <h3 className="font-headline-md text-[18px] leading-tight text-primary">Board Briefing Signature Required</h3>
                    <span className="px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-label-sm text-[10px] uppercase">Legal</span>
                  </div>
                  <p className="font-body-md text-on-surface-variant">Q4 Strategic Pivot document is ready for final executive sign-off prior to distribution.</p>
                  <div className="flex items-center space-x-4 mt-3 text-on-surface-variant/60 font-label-sm text-[11px]">
                    <span className="flex items-center"><span className="material-symbols-outlined text-[14px] mr-1">schedule</span> 2 hours ago</span>
                    <span className="flex items-center"><span className="material-symbols-outlined text-[14px] mr-1">timer</span> Due: Today 17:00</span>
                  </div>
                </div>
              </div>
              <button className="px-4 py-2 bg-primary text-on-primary font-label-md text-label-md rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200">Review</button>
            </div>
          </div>
        </section>

        {/* AI Insights Section */}
        <section className="pt-2 animate-in fade-in slide-in-from-bottom-2 duration-300 delay-150">
          <h2 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest mb-4 flex items-center">
            <span className="material-symbols-outlined text-[14px] text-tertiary-fixed-dim mr-2">auto_awesome</span> AI Insights
          </h2>
          
          <div className="glass-card rounded-xl p-6 cursor-pointer relative overflow-hidden group" style={{ background: "linear-gradient(145deg, rgba(255,255,255,0.8) 0%, rgba(218, 226, 253, 0.15) 100%)", backdropFilter: "blur(12px)" }}>
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4">
                <div className="p-2 bg-tertiary-fixed/40 rounded-lg text-tertiary mt-1">
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>smart_toy</span>
                </div>
                <div>
                  <div className="flex items-center space-x-3 mb-1">
                    <h3 className="font-headline-md text-[18px] leading-tight text-primary">Weekly Intelligence Summary Generated</h3>
                    <span className="px-2 py-0.5 rounded-full bg-surface-variant text-on-surface-variant font-label-sm text-[10px] uppercase">Synthesis</span>
                  </div>
                  <p className="font-body-md text-on-surface-variant">Synthesis of 45 high-priority communications and 3 board papers now available for review.</p>
                  <div className="flex items-center space-x-4 mt-3 text-on-surface-variant/60 font-label-sm text-[11px]">
                    <span className="flex items-center"><span className="material-symbols-outlined text-[14px] mr-1">schedule</span> 4 hours ago</span>
                    <span className="flex items-center"><span className="material-symbols-outlined text-[14px] mr-1">read_more</span> 3 min read</span>
                  </div>
                </div>
              </div>
              <span className="material-symbols-outlined text-outline-variant group-hover:text-primary transition-colors">arrow_forward</span>
            </div>
          </div>
        </section>
      </div>

      {/* Context / Widget Column */}
      <div className="lg:col-span-4 hidden lg:block space-y-6">
        {/* System Status Widget */}
        <div className="glass-card rounded-xl p-6">
          <h3 className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-widest border-b border-outline-variant/20 pb-3 mb-4">
            System Status
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="font-body-md text-primary">Critical Anomalies</span>
              <span className="font-label-md font-bold text-error">1</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="font-body-md text-primary">Pending Actions</span>
              <span className="font-label-md font-bold text-secondary">4</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="font-body-md text-primary">AI Syntheses</span>
              <span className="font-label-md font-bold text-on-surface-variant">12</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
