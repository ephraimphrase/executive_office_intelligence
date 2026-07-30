"use client";

import React, { useEffect, useState } from "react";
import { Meeting, fetchCommitteeMeetings } from "@/lib/api";
import CalendarViewSwitcher, { CalendarViewMode } from "./CalendarViewSwitcher";

interface CommitteeViewProps {
  view: CalendarViewMode;
  onChangeView: (view: CalendarViewMode) => void;
}

const TYPE_LABELS: Record<string, string> = {
  BOARD: "Board",
  EXECUTIVE_COMMITTEE: "Executive Committee",
};

export default function CommitteeView({ view, onChangeView }: CommitteeViewProps) {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    let cancelled = false;
    fetchCommitteeMeetings().then((result) => {
      if (!cancelled) {
        setMeetings(result);
        setLoaded(true);
      }
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const upcoming = meetings.filter((m) => new Date(m.meeting_date) >= new Date(new Date().toDateString()));
  const past = meetings.filter((m) => new Date(m.meeting_date) < new Date(new Date().toDateString()));

  const renderRow = (meeting: Meeting) => (
    <div
      key={meeting.id}
      className="flex items-center gap-4 p-4 bg-white border border-outline-variant/10 rounded-lg hover:shadow-sm transition-shadow"
    >
      <div className="w-14 h-14 rounded-lg bg-primary/5 flex flex-col items-center justify-center shrink-0">
        <span className="font-label-sm text-primary uppercase">
          {new Date(meeting.meeting_date).toLocaleDateString(undefined, { month: "short" })}
        </span>
        <span className="font-headline-md text-primary">{new Date(meeting.meeting_date).getDate()}</span>
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-label-md text-primary font-semibold truncate">{meeting.title}</p>
        <p className="font-label-sm text-on-surface-variant">
          {TYPE_LABELS[meeting.meeting_type] || meeting.meeting_type}
          {meeting.chairperson ? ` • Chaired by ${meeting.chairperson}` : ""}
          {meeting.location ? ` • ${meeting.location}` : ""}
        </p>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        {meeting.board_paper_required && (
          <span
            className={`inline-flex items-center px-2 py-1 rounded text-xs font-semibold border ${
              meeting.board_paper_submitted
                ? "bg-primary-fixed text-on-primary-fixed-variant border-primary-fixed-dim/50"
                : "bg-error-container text-on-error-container border-error/20"
            }`}
          >
            {meeting.board_paper_submitted ? "Board Paper Submitted" : "Board Paper Due"}
          </span>
        )}
        <span className="font-label-sm text-on-surface-variant px-2 py-1 bg-surface-container rounded">
          {meeting.status}
        </span>
      </div>
    </div>
  );

  return (
    <div className="w-full p-8 h-full overflow-y-auto no-scrollbar">
      <div className="flex justify-between items-center mb-8">
        <h3 className="font-headline-lg text-headline-lg text-primary">Committee Calendar</h3>
        <CalendarViewSwitcher view={view} onChange={onChangeView} />
      </div>

      {!loaded ? (
        <p className="font-label-md text-on-surface-variant">Loading…</p>
      ) : meetings.length === 0 ? (
        <p className="font-label-md text-on-surface-variant">No Board or Executive Committee meetings on file.</p>
      ) : (
        <div className="space-y-8">
          <section>
            <h4 className="font-label-sm text-primary font-bold uppercase tracking-wider mb-4">Upcoming</h4>
            {upcoming.length === 0 ? (
              <p className="font-label-sm text-on-surface-variant">No upcoming committee meetings scheduled.</p>
            ) : (
              <div className="space-y-3">{upcoming.map(renderRow)}</div>
            )}
          </section>

          {past.length > 0 && (
            <section>
              <h4 className="font-label-sm text-primary font-bold uppercase tracking-wider mb-4">Past</h4>
              <div className="space-y-3 opacity-70">{past.map(renderRow)}</div>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
