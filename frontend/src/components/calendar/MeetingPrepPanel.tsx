"use client";

import React, { useEffect, useState } from "react";
import { EventItem } from "@/components/dashboard/ScheduleWidget";
import { EventPrep, fetchEventPrep } from "@/lib/api";

interface MeetingPrepPanelProps {
  selectedEvent: EventItem | null;
}

export default function MeetingPrepPanel({ selectedEvent }: MeetingPrepPanelProps) {
  const [prep, setPrep] = useState<EventPrep | null>(null);

  useEffect(() => {
    if (!selectedEvent) return;
    let cancelled = false;
    fetchEventPrep(selectedEvent.id).then((result) => {
      if (!cancelled) setPrep(result);
    });
    return () => {
      cancelled = true;
    };
  }, [selectedEvent]);

  // Considered "loading" whenever the fetched prep hasn't caught up to the
  // currently selected event yet (also covers switching directly between
  // two events without an intermediate deselect).
  const isLoading = selectedEvent !== null && prep?.event_id !== selectedEvent.id;

  if (!selectedEvent) {
    return (
      <aside className="w-[30%] h-full p-8 glass-panel border-l border-outline-variant/20 flex flex-col justify-center items-center overflow-y-auto no-scrollbar">
        <span className="material-symbols-outlined text-[48px] text-on-surface-variant/50 mb-4">
          calendar_month
        </span>
        <p className="font-label-md text-on-surface-variant text-center">
          Select an event in the calendar to view preparation materials.
        </p>
      </aside>
    );
  }

  const isCritical = selectedEvent.priority === "CRITICAL";
  const currentPrep = isLoading ? null : prep;
  const agenda = currentPrep?.agenda ?? [];
  const attendees = currentPrep?.attendees ?? [];
  const talkingPoints = currentPrep?.talking_points ?? [];
  const documents = currentPrep?.documents ?? [];

  return (
    <aside className="w-[30%] h-full p-8 glass-panel border-l border-outline-variant/20 flex flex-col overflow-y-auto no-scrollbar">
      <div className="mb-8">
        {isCritical && (
          <span className="inline-block px-3 py-1 bg-error text-on-primary text-[10px] font-bold rounded-full mb-3 tracking-widest">
            CRITICAL PREP
          </span>
        )}
        <h3 className="font-headline-md text-primary mb-2">Meeting Prep: {selectedEvent.title}</h3>
        <p className="font-label-sm text-on-surface-variant flex items-center gap-2">
          <span className="material-symbols-outlined text-[16px]">schedule</span>
          {selectedEvent.time} • {selectedEvent.location}
        </p>
      </div>

      {/* Agenda Section */}
      <section className="mb-8">
        <h4 className="font-label-sm text-primary font-bold uppercase tracking-wider mb-4 border-b border-outline-variant/10 pb-2">
          Agenda Items
        </h4>
        {isLoading ? (
          <p className="font-label-sm text-on-surface-variant">Loading…</p>
        ) : agenda.length === 0 ? (
          <p className="font-label-sm text-on-surface-variant">No agenda set for this event.</p>
        ) : (
          <ul className="space-y-3">
            {agenda.map((item, i) => (
              <li key={i} className="flex gap-3">
                <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 shrink-0"></span>
                <p className="font-body-md text-on-surface-variant">{item}</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Key Attendees */}
      <section className="mb-8">
        <h4 className="font-label-sm text-primary font-bold uppercase tracking-wider mb-4 border-b border-outline-variant/10 pb-2">
          Key Attendees
        </h4>
        {attendees.length === 0 ? (
          <p className="font-label-sm text-on-surface-variant">No attendees listed.</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {attendees.map((name, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface-container text-label-sm text-on-surface-variant"
              >
                <span className="material-symbols-outlined text-[16px]">person</span>
                {name}
              </span>
            ))}
          </div>
        )}
      </section>

      {/* AI Insights */}
      <section className="mb-8 p-5 bg-primary/5 rounded-xl border border-primary/10 relative overflow-hidden">
        <div className="absolute -right-4 -top-4 opacity-5">
          <span className="material-symbols-outlined text-[80px]">auto_awesome</span>
        </div>
        <h4 className="font-label-sm text-primary font-bold uppercase tracking-wider mb-3 flex items-center gap-2">
          <span className="material-symbols-outlined text-[18px]">smart_toy</span>
          AI Talking Points
        </h4>
        {talkingPoints.length === 0 ? (
          <p className="font-body-md text-primary/80 italic leading-relaxed">
            {isLoading ? "Generating…" : "No AI talking points available for this meeting."}
          </p>
        ) : (
          <ul className="space-y-2">
            {talkingPoints.map((point, i) => (
              <li key={i} className="font-body-md text-primary/80 leading-relaxed">
                {point}
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* Documents */}
      <section>
        <h4 className="font-label-sm text-primary font-bold uppercase tracking-wider mb-4 border-b border-outline-variant/10 pb-2">
          Reference Documents
        </h4>
        {documents.length === 0 ? (
          <p className="font-label-sm text-on-surface-variant">No related documents found.</p>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <a
                key={doc.id}
                className="flex items-center gap-3 p-3 bg-white hover:bg-surface-container-low border border-outline-variant/10 rounded-lg transition-colors group cursor-pointer"
              >
                <span className="material-symbols-outlined text-on-surface-variant group-hover:text-primary">
                  description
                </span>
                <div className="flex-1 min-w-0">
                  <p className="font-label-md text-primary font-semibold truncate">{doc.title}</p>
                  {doc.snippet && (
                    <p className="font-label-sm text-on-surface-variant truncate">{doc.snippet}</p>
                  )}
                </div>
                <span className="material-symbols-outlined text-on-surface-variant/40">chevron_right</span>
              </a>
            ))}
          </div>
        )}
      </section>

      {/* Panel Footer Action */}
      <div className="mt-auto pt-8">
        <button className="w-full py-4 bg-primary text-on-primary rounded-xl font-headline-md text-[16px] hover:bg-primary-container transition-all active:scale-95 flex items-center justify-center gap-2">
          <span className="material-symbols-outlined">video_call</span>
          Join Virtual Room
        </button>
      </div>
    </aside>
  );
}
