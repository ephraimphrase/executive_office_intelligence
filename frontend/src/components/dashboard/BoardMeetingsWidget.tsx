import React from "react";
import type { Event } from "@/lib/api";

interface BoardMeetingsWidgetProps {
  meetings: Event[];
}

export default function BoardMeetingsWidget({ meetings }: BoardMeetingsWidgetProps) {
  return (
    <section className="glass-card rounded-xl p-6">
      <h2 className="font-headline-md text-headline-md text-primary flex items-center gap-2 mb-6">
        <span className="material-symbols-outlined text-[24px]">groups_2</span>
        Upcoming Board Meetings
      </h2>

      {meetings.length === 0 ? (
        <p className="font-label-md text-label-md text-on-surface-variant">No board meetings scheduled.</p>
      ) : (
        <div className="space-y-3">
          {meetings.map((event) => (
            <div key={event.id} className="flex justify-between items-center gap-3 py-2 border-b border-slate-100 last:border-0">
              <div className="flex items-center gap-2 min-w-0">
                <span className="material-symbols-outlined text-[18px] text-on-surface-variant shrink-0">
                  event
                </span>
                <p className="font-label-md text-label-md font-medium text-on-surface truncate">{event.title}</p>
              </div>
              <span className="font-label-sm text-label-sm text-on-surface-variant whitespace-nowrap">
                {new Date(event.start_datetime).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
              </span>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
