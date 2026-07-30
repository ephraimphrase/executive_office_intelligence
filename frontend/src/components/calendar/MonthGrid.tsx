"use client";

import React, { useEffect, useMemo, useState } from "react";
import { EventItem } from "@/components/dashboard/ScheduleWidget";
import { fetchEventsInRange } from "@/lib/api";
import CalendarViewSwitcher, { CalendarViewMode } from "./CalendarViewSwitcher";

interface MonthGridProps {
  onSelectEvent: (event: EventItem) => void;
  view: CalendarViewMode;
  onChangeView: (view: CalendarViewMode) => void;
}

function toEventItem(e: {
  id: string;
  title: string;
  start_datetime: string;
  end_datetime: string;
  location: string | null;
  event_type: string;
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
}): EventItem {
  const start = new Date(e.start_datetime);
  const end = new Date(e.end_datetime);
  const time = `${start.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })} - ${end.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
  return {
    id: e.id,
    title: e.title,
    time,
    location: e.location || "TBD",
    type: e.event_type,
    priority: e.priority,
    start_datetime: e.start_datetime,
  };
}

function dateKey(date: Date): string {
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
}

export default function MonthGrid({ onSelectEvent, view, onChangeView }: MonthGridProps) {
  const [monthAnchor, setMonthAnchor] = useState(() => {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), 1);
  });
  const [events, setEvents] = useState<EventItem[]>([]);

  // Calendar grid always shows full weeks (Mon-start), so it can spill into
  // the trailing days of the previous/next month.
  const gridStart = useMemo(() => {
    const first = new Date(monthAnchor);
    const day = first.getDay();
    const diffToMonday = day === 0 ? -6 : 1 - day;
    first.setDate(first.getDate() + diffToMonday);
    first.setHours(0, 0, 0, 0);
    return first;
  }, [monthAnchor]);

  const days = useMemo(
    () => Array.from({ length: 42 }).map((_, i) => new Date(gridStart.getTime() + i * 86400000)),
    [gridStart]
  );

  useEffect(() => {
    let cancelled = false;
    const rangeStart = days[0];
    const rangeEnd = days[days.length - 1];
    const isoStart = rangeStart.toISOString();
    const isoEnd = new Date(rangeEnd.getTime() + 86400000 - 1).toISOString();

    fetchEventsInRange(isoStart, isoEnd).then((result) => {
      if (!cancelled) setEvents(result.map(toEventItem));
    });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [monthAnchor]);

  const eventsByDay = useMemo(() => {
    const map = new Map<string, EventItem[]>();
    for (const event of events) {
      if (!event.start_datetime) continue;
      const key = dateKey(new Date(event.start_datetime));
      const list = map.get(key) || [];
      list.push(event);
      map.set(key, list);
    }
    return map;
  }, [events]);

  const monthLabel = monthAnchor.toLocaleDateString(undefined, { month: "long", year: "numeric" });
  const today = new Date();

  const goToPrevMonth = () => setMonthAnchor((m) => new Date(m.getFullYear(), m.getMonth() - 1, 1));
  const goToNextMonth = () => setMonthAnchor((m) => new Date(m.getFullYear(), m.getMonth() + 1, 1));

  return (
    <div className="w-[70%] p-8 h-full overflow-y-auto no-scrollbar">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center gap-4">
          <button onClick={goToPrevMonth} className="p-2 hover:bg-surface-container rounded-lg transition-colors">
            <span className="material-symbols-outlined">chevron_left</span>
          </button>
          <h3 className="font-headline-lg text-headline-lg text-primary">{monthLabel}</h3>
          <button onClick={goToNextMonth} className="p-2 hover:bg-surface-container rounded-lg transition-colors">
            <span className="material-symbols-outlined">chevron_right</span>
          </button>
        </div>
        <CalendarViewSwitcher view={view} onChange={onChangeView} />
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-outline-variant/10 overflow-hidden grid grid-cols-7">
        {["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"].map((label, i) => (
          <div
            key={label}
            className={`text-center py-3 font-label-sm text-on-surface-variant bg-surface-container-low/30 border-b border-outline-variant/10 ${i < 6 ? "border-r" : ""}`}
          >
            {label}
          </div>
        ))}

        {days.map((date, i) => {
          const inMonth = date.getMonth() === monthAnchor.getMonth();
          const isToday = date.toDateString() === today.toDateString();
          const dayEvents = eventsByDay.get(dateKey(date)) || [];

          return (
            <div
              key={i}
              className={`min-h-[100px] p-2 border-b border-outline-variant/5 ${(i + 1) % 7 !== 0 ? "border-r" : ""} ${inMonth ? "" : "bg-surface-container-low/20"}`}
            >
              <span
                className={`inline-flex items-center justify-center w-6 h-6 rounded-full font-label-sm ${
                  isToday ? "bg-primary text-on-primary font-bold" : inMonth ? "text-on-surface" : "text-on-surface-variant/40"
                }`}
              >
                {date.getDate()}
              </span>
              <div className="mt-1 space-y-1">
                {dayEvents.slice(0, 3).map((event) => (
                  <button
                    key={event.id}
                    onClick={() => onSelectEvent(event)}
                    className={`w-full text-left px-1.5 py-0.5 rounded text-label-sm truncate transition-colors ${
                      event.priority === "CRITICAL"
                        ? "bg-error/10 text-error hover:bg-error/20"
                        : "bg-primary/5 text-primary hover:bg-primary/10"
                    }`}
                  >
                    {event.title}
                  </button>
                ))}
                {dayEvents.length > 3 && (
                  <p className="font-label-sm text-on-surface-variant px-1.5">+{dayEvents.length - 3} more</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
