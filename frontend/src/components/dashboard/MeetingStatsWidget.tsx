import React from "react";
import type { MeetingStats } from "@/lib/api";

interface MeetingStatsWidgetProps {
  stats: MeetingStats;
}

export default function MeetingStatsWidget({ stats }: MeetingStatsWidgetProps) {
  return (
    <section className="glass-card rounded-xl p-6">
      <h2 className="font-headline-md text-headline-md text-primary flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-[24px]">query_stats</span>
        Meeting Statistics
      </h2>

      <div className="flex items-baseline gap-3">
        <span className="font-headline-lg text-headline-lg text-primary">{stats.total_meetings}</span>
        <span className="font-label-md text-label-md text-on-surface-variant">
          meetings from {stats.period.from} to {stats.period.to}
        </span>
      </div>
    </section>
  );
}
