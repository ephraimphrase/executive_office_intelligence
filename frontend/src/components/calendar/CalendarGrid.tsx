"use client";

import React, { useMemo, useState } from "react";
import { EventItem } from "@/components/dashboard/ScheduleWidget";
import { createEvent } from "@/lib/api";
import CalendarViewSwitcher, { CalendarViewMode } from "./CalendarViewSwitcher";

interface CalendarGridProps {
  events: EventItem[];
  onSelectEvent: (event: EventItem) => void;
  view: CalendarViewMode;
  onChangeView: (view: CalendarViewMode) => void;
}

const HOURS = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17];
const WEEKDAY_LABELS = ["MON", "TUE", "WED", "THU", "FRI"];

function startOfWeek(date: Date): Date {
  const monday = new Date(date);
  const day = monday.getDay(); // 0 = Sun, 1 = Mon, ...
  const diffToMonday = day === 0 ? -6 : 1 - day;
  monday.setDate(monday.getDate() + diffToMonday);
  monday.setHours(0, 0, 0, 0);
  return monday;
}

function dayIndexInWeek(monday: Date, eventDate: Date): number {
  const eventDay = new Date(eventDate);
  eventDay.setHours(0, 0, 0, 0);
  return Math.round((eventDay.getTime() - monday.getTime()) / 86400000);
}

export default function CalendarGrid({ events, onSelectEvent, view, onChangeView }: CalendarGridProps) {
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const monday = useMemo(() => startOfWeek(new Date()), []);
  const weekDates = useMemo(
    () => Array.from({ length: 5 }).map((_, i) => new Date(monday.getTime() + i * 86400000)),
    [monday]
  );
  const weekLabel = `${weekDates[0].toLocaleDateString(undefined, { month: "long", day: "numeric" })} – ${weekDates[4].toLocaleDateString(undefined, { day: "numeric", year: "numeric" })}`;

  // Bucket events into (hour, weekday) cells for this Mon–Fri grid. Events
  // outside the displayed hour range or week don't have a cell to render
  // into — a known limit of this fixed 8am–6pm business-week view.
  const eventsByCell = useMemo(() => {
    const map = new Map<string, EventItem>();
    for (const event of events) {
      if (!event.start_datetime) continue;
      const start = new Date(event.start_datetime);
      const dayIndex = dayIndexInWeek(monday, start);
      const hour = start.getHours();
      if (dayIndex < 0 || dayIndex > 4 || !HOURS.includes(hour)) continue;
      map.set(`${hour}-${dayIndex}`, event);
    }
    return map;
  }, [events, monday]);

  const handleSelect = (event: EventItem) => {
    setSelectedEventId(event.id);
    onSelectEvent(event);
  };

  const handleCreateEvent = async () => {
    const title = prompt("Enter event title:");
    if (!title) return;

    try {
      setIsCreating(true);
      const newEventData = {
        title,
        start_datetime: new Date().toISOString(),
        end_datetime: new Date(Date.now() + 3600000).toISOString(),
        location: "Virtual",
        event_type: "MEETING" as const,
        priority: "MEDIUM" as const,
      };

      const created = await createEvent(newEventData);
      alert(`Event created successfully with ID: ${created.id}`);
      // Ideally, trigger a refresh of the events list here.
    } catch {
      alert("Failed to create event. Ensure backend is running.");
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <div className="w-[70%] p-8 h-full overflow-y-auto no-scrollbar">
      <div className="flex justify-between items-center mb-8">
        <div className="flex items-center gap-4">
          <button className="p-2 hover:bg-surface-container rounded-lg transition-colors">
            <span className="material-symbols-outlined">chevron_left</span>
          </button>
          <h3 className="font-headline-lg text-headline-lg text-primary">{weekLabel}</h3>
          <button className="p-2 hover:bg-surface-container rounded-lg transition-colors">
            <span className="material-symbols-outlined">chevron_right</span>
          </button>
        </div>
        <CalendarViewSwitcher view={view} onChange={onChangeView} />
        <button 
          onClick={handleCreateEvent}
          disabled={isCreating}
          className="px-4 py-2 bg-primary text-on-primary font-label-md rounded-lg flex items-center gap-2 hover:bg-primary/90 transition-colors"
        >
          <span className="material-symbols-outlined text-[18px]">add</span>
          New Event
        </button>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-outline-variant/10 overflow-hidden">
        <div className="calendar-grid">
          {/* Header Empty Corner */}
          <div className="border-b border-r border-outline-variant/10 h-16"></div>

          {/* Weekday Headers */}
          {weekDates.map((date, i) => (
            <div
              key={i}
              className={`border-b border-outline-variant/10 flex flex-col justify-center items-center h-16 bg-surface-container-low/30 ${i < 4 ? "border-r" : ""}`}
            >
              <span className="font-label-sm text-on-surface-variant">{WEEKDAY_LABELS[i]}</span>
              <span className="font-headline-md text-primary">{date.getDate()}</span>
            </div>
          ))}

          {/* Hour Markers & Slots */}
          {HOURS.map((hour) => (
            <React.Fragment key={hour}>
              <div className="border-r border-b border-outline-variant/5 flex justify-end pr-4 pt-2 font-label-sm text-on-surface-variant/70">
                {hour}:00
              </div>

              {/* 5 columns for Mon-Fri */}
              {[0, 1, 2, 3, 4].map((dayIndex) => {
                const event = eventsByCell.get(`${hour}-${dayIndex}`);
                const isActive = event ? selectedEventId === event.id : false;
                const isCritical = event?.priority === "CRITICAL";
                const eventClasses = event
                  ? `${isCritical ? "bg-error/10 border-l-4 border-error hover:bg-error/20" : "bg-primary/5 border-l-4 border-primary hover:bg-primary/10"} rounded-lg p-3 cursor-pointer transition-all shadow-sm z-10 ${isActive ? "ring-2 ring-primary/20 scale-[1.02]" : ""}`
                  : "";

                return (
                  <div key={`${hour}-${dayIndex}`} className={`border-b border-outline-variant/5 relative ${dayIndex < 4 ? "border-r" : ""}`}>
                    {event && (
                      <div className={`absolute inset-x-2 top-0 h-[80px] ${eventClasses}`}>
                        <div onClick={() => handleSelect(event)}>
                          <p className={`font-label-sm font-bold mb-1 ${isCritical ? "text-error" : "text-primary"}`}>
                            {event.priority}
                          </p>
                          <h4 className="font-label-md text-primary font-bold leading-tight">{event.title}</h4>
                          <p className="font-label-sm text-on-surface-variant">{event.time}</p>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}
