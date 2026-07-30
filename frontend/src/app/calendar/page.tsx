import React from "react";
import CalendarClient from "./CalendarClient";
import { fetchWeekEvents } from "@/lib/api";
import { getServerCookieHeader } from "@/lib/server-cookies";
import { EventItem } from "@/components/dashboard/ScheduleWidget";

export default async function CalendarPage() {
  const cookieHeader = await getServerCookieHeader();
  const eventsData = await fetchWeekEvents(cookieHeader);

  const events: EventItem[] = eventsData.map((e) => {
    const start = new Date(e.start_datetime);
    const end = new Date(e.end_datetime);
    const timeString = `${start.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    })} - ${end.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
    return {
      id: e.id,
      title: e.title,
      time: timeString,
      location: e.location || "TBD",
      type: e.event_type,
      priority: e.priority,
      start_datetime: e.start_datetime,
    };
  });

  return <CalendarClient events={events} />;
}
