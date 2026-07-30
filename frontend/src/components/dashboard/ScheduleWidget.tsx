import React from "react";

export interface EventItem {
  id: string;
  title: string;
  time: string;
  location: string;
  type: string;
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  isPast?: boolean;
  // Raw ISO timestamp, additionally carried alongside the pre-formatted
  // `time` string so weekly-grid views (CalendarGrid) can bucket events by
  // actual weekday/hour instead of just displaying them in a flat list.
  start_datetime?: string;
}

interface ScheduleWidgetProps {
  events: EventItem[];
  title?: string;
}

export default function ScheduleWidget({ events, title = "Today's Schedule" }: ScheduleWidgetProps) {
  return (
    <section className="glass-card rounded-xl p-6">
      <div className="flex justify-between items-center mb-6 pb-4 border-b border-slate-100">
        <h2 className="font-headline-md text-headline-md text-primary flex items-center gap-2">
          <span className="material-symbols-outlined text-[24px]">
            view_timeline
          </span>
          {title}
        </h2>
        <button className="font-label-md text-label-md text-on-surface-variant hover:text-primary transition-colors flex items-center gap-1">
          View Full Calendar{" "}
          <span className="material-symbols-outlined text-[16px]">
            arrow_forward
          </span>
        </button>
      </div>

      <div className="relative pl-4 border-l-2 border-slate-100 space-y-6">
        {events.map((event) => (
          <div key={event.id} className="relative group cursor-pointer">
            <div
              className={`absolute -left-[21px] top-1 w-3 h-3 rounded-full border-2 transition-colors ${
                event.priority === "CRITICAL"
                  ? "bg-primary border-white"
                  : "bg-white border-slate-300 group-hover:border-primary"
              }`}
            ></div>

            <div
              className={`transition-all ${
                event.priority === "CRITICAL"
                  ? "bg-surface-container-low rounded-lg p-4 group-hover:bg-white group-hover:shadow-sm border border-transparent group-hover:border-slate-200"
                  : "pl-2 group-hover:pl-4"
              }`}
            >
              <div className="flex flex-wrap justify-between items-start gap-4 mb-2">
                <div>
                  <h4
                    className={`font-label-md text-label-md ${
                      event.priority === "CRITICAL"
                        ? "font-semibold text-primary"
                        : "font-medium text-on-surface"
                    }`}
                  >
                    {event.title}
                  </h4>
                  <p className="font-label-sm text-label-sm text-on-surface-variant mt-1 flex items-center gap-1">
                    <span className="material-symbols-outlined text-[14px]">
                      schedule
                    </span>{" "}
                    {event.time}
                  </p>
                </div>

                {event.priority === "CRITICAL" && (
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs font-semibold bg-error-container text-on-error-container border border-error/20">
                    CRITICAL
                  </span>
                )}
              </div>

              {event.priority === "CRITICAL" && (
                <div className="flex items-center gap-4 mt-3 pt-3 border-t border-slate-100">
                  <span className="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-1">
                    <span className="material-symbols-outlined text-[14px]">
                      location_on
                    </span>{" "}
                    {event.location}
                  </span>
                  <span className="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-1">
                    <span className="material-symbols-outlined text-[14px]">
                      meeting_room
                    </span>{" "}
                    {event.type}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
