"use client";

import React, { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import CalendarGrid from "@/components/calendar/CalendarGrid";
import MonthGrid from "@/components/calendar/MonthGrid";
import CommitteeView from "@/components/calendar/CommitteeView";
import MeetingPrepPanel from "@/components/calendar/MeetingPrepPanel";
import { CalendarViewMode } from "@/components/calendar/CalendarViewSwitcher";
import { EventItem } from "@/components/dashboard/ScheduleWidget";

interface CalendarClientProps {
  events: EventItem[];
}

export default function CalendarClient({ events }: CalendarClientProps) {
  const [selectedEvent, setSelectedEvent] = useState<EventItem | null>(null);
  const [view, setView] = useState<CalendarViewMode>("week");

  return (
    <>
      <Sidebar />
      <TopNav title="Calendar Intelligence" />
      <main className="md:pl-64 pt-20 h-screen overflow-hidden flex flex-col md:flex-row">
        {view === "committee" ? (
          <CommitteeView view={view} onChangeView={setView} />
        ) : (
          <>
            {view === "week" ? (
              <CalendarGrid events={events} onSelectEvent={setSelectedEvent} view={view} onChangeView={setView} />
            ) : (
              <MonthGrid onSelectEvent={setSelectedEvent} view={view} onChangeView={setView} />
            )}
            <MeetingPrepPanel selectedEvent={selectedEvent} />
          </>
        )}
      </main>
    </>
  );
}
