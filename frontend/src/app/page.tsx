import React from "react";
import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";
import WelcomeHeader from "@/components/dashboard/WelcomeHeader";
import MetricCard from "@/components/dashboard/MetricCard";
import ScheduleWidget, { EventItem } from "@/components/dashboard/ScheduleWidget";
import DecisionsWidget, { DecisionItem } from "@/components/dashboard/DecisionsWidget";
import InsightsWidget, { InsightItem } from "@/components/dashboard/InsightsWidget";
import CriticalCommsWidget, { EmailItem } from "@/components/dashboard/CriticalCommsWidget";
import RiskRegisterWidget from "@/components/dashboard/RiskRegisterWidget";
import FollowUpRegisterWidget from "@/components/dashboard/FollowUpRegisterWidget";
import BoardPaperTrackerWidget from "@/components/dashboard/BoardPaperTrackerWidget";
import WaitingForWidget from "@/components/dashboard/WaitingForWidget";
import DepartmentStatusWidget from "@/components/dashboard/DepartmentStatusWidget";
import UrgentMattersWidget, { UrgentMatter } from "@/components/dashboard/UrgentMattersWidget";
import BoardMeetingsWidget from "@/components/dashboard/BoardMeetingsWidget";
import MeetingStatsWidget from "@/components/dashboard/MeetingStatsWidget";

import {
  fetchEvents,
  fetchDecisions,
  fetchEmails,
  fetchTasks,
  fetchOpenRisks,
  fetchCommitmentsDueSoon,
  fetchBoardPapers,
  fetchWaitingForMe,
  fetchWaitingForOthers,
  fetchOverdueTasks,
  fetchTaskStats,
  fetchDecisionStats,
  fetchEmailStats,
  fetchDepartmentTaskReport,
  fetchRecentDecisions,
  fetchTomorrowEvents,
  fetchUpcomingBoardMeetings,
  fetchMeetingStats,
} from "@/lib/api";
import { getServerCookieHeader } from "@/lib/server-cookies";

export default async function DashboardPage() {
  // Forward the visitor's session cookie — this is a Server Component, so
  // these fetches run on the Next.js server, not in the browser, and won't
  // carry the user's auth cookie unless we attach it explicitly.
  const cookieHeader = await getServerCookieHeader();

  // Fetch data in parallel
  const [
    eventsData,
    decisionsData,
    emailsData,
    tasksData,
    risksData,
    commitmentsData,
    boardPapersData,
    waitingForMeData,
    waitingForOthersData,
    overdueTasksData,
    taskStats,
    decisionStats,
    emailStats,
    departmentReport,
    recentDecisionsData,
    tomorrowEventsData,
    upcomingBoardMeetingsData,
    meetingStats,
  ] = await Promise.all([
    fetchEvents(cookieHeader),
    fetchDecisions(cookieHeader),
    fetchEmails(cookieHeader),
    fetchTasks(cookieHeader),
    fetchOpenRisks(cookieHeader),
    fetchCommitmentsDueSoon(cookieHeader),
    fetchBoardPapers(cookieHeader),
    fetchWaitingForMe(cookieHeader),
    fetchWaitingForOthers(cookieHeader),
    fetchOverdueTasks(cookieHeader),
    fetchTaskStats(cookieHeader),
    fetchDecisionStats(cookieHeader),
    fetchEmailStats(cookieHeader),
    fetchDepartmentTaskReport(cookieHeader),
    fetchRecentDecisions(cookieHeader),
    fetchTomorrowEvents(cookieHeader),
    fetchUpcomingBoardMeetings(cookieHeader),
    fetchMeetingStats(cookieHeader),
  ]);

  // Map Backend Data to Component Props
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
    };
  });

  const tomorrowEvents: EventItem[] = tomorrowEventsData.map((e) => {
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
    };
  });

  const decisions: DecisionItem[] = decisionsData.map((d) => ({
    id: d.id,
    title: d.title,
    description: d.description,
    status: d.status,
    priority: d.priority,
    dueDate: d.due_date
      ? new Date(d.due_date).toLocaleDateString(undefined, {
          month: "short",
          day: "numeric",
        })
      : null,
  }));

  const recentDecisions: DecisionItem[] = recentDecisionsData.map((d) => ({
    id: d.id,
    title: d.title,
    description: d.description,
    status: d.status,
    priority: d.priority,
    dueDate: d.due_date
      ? new Date(d.due_date).toLocaleDateString(undefined, { month: "short", day: "numeric" })
      : null,
  }));

  const emails: EmailItem[] = emailsData.map((e) => {
    const received = new Date(e.received_at);
    // Rough formatting for time (e.g. 08:15 AM or "Yesterday")
    const today = new Date();
    const isToday = received.toDateString() === today.toDateString();
    const timeStr = isToday
      ? received.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
      : "Yesterday";

    return {
      id: e.id,
      sender: e.sender_name,
      subject: e.subject,
      time: timeStr,
      isUnread: e.status === "UNREAD",
    };
  });

  const insight: InsightItem = {
    type: "RISK",
    title: "Risk Detected",
    description:
      "Supply chain disruption in Southeast Asia may impact Q3 targets for the Electronics division. Recommend immediate review of alternative sourcing.",
  };

  const taskCompletionPct = taskStats.total
    ? Math.round(((taskStats.by_status["DONE"] || 0) / taskStats.total) * 100)
    : 0;

  // Urgent Matters: critical unread emails + overdue tasks + open critical/high risks
  const urgentMatters: UrgentMatter[] = [
    ...emailsData
      .filter((e) => e.priority === "URGENT" && e.status === "UNREAD")
      .map((e) => ({ id: e.id, label: e.subject, category: "Email" as const })),
    ...overdueTasksData.map((t) => ({ id: t.id, label: `Overdue: ${t.title}`, category: "Task" as const })),
    ...risksData
      .filter((r) => r.severity === "CRITICAL" || r.severity === "HIGH")
      .map((r) => ({ id: r.id, label: r.description, category: "Risk" as const })),
  ];

  return (
    <>
      <Sidebar />
      <TopNav />
      <main className="pt-28 pb-12 px-margin-mobile md:px-margin-desktop md:ml-64 max-w-container-max mx-auto">
        <WelcomeHeader />

        {/* Metric Cards */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter mb-6">
          <MetricCard
            title="Meetings Today"
            value={eventsData.length}
            icon="groups"
          />
          <MetricCard
            title="Outstanding Tasks"
            value={tasksData.length}
            icon="check_circle"
            trend="-2 from yesterday"
          />
          <MetricCard
            title="Critical Unread Emails"
            value={emailsData.filter((e) => e.priority === "URGENT" && e.status === "UNREAD").length || emails.length}
            icon="mail"
            iconBgColor="bg-error-container"
            iconTextColor="text-on-error-container group-hover:bg-error group-hover:text-white"
            valueColor="text-error"
            hasAlertBackground
          />
          <MetricCard
            title="Pending Approvals"
            value={decisionsData.length}
            icon="gavel"
          />
        </section>

        {/* Executive KPIs */}
        <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-gutter mb-12">
          <MetricCard
            title="Email Response Rate"
            value={emailStats.response_rate}
            icon="reply"
          />
          <MetricCard
            title="Task Completion"
            value={`${taskCompletionPct}%`}
            icon="task_alt"
          />
          <MetricCard
            title="Decisions Implemented"
            value={decisionStats.implemented}
            icon="verified"
          />
          <MetricCard
            title="Open Risks"
            value={risksData.length}
            icon="warning"
            iconBgColor={risksData.length > 0 ? "bg-error-container" : undefined}
            iconTextColor={risksData.length > 0 ? "text-on-error-container" : undefined}
          />
        </section>

        {/* Widgets Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-gutter mb-gutter">
          <div className="lg:col-span-2 flex flex-col gap-gutter">
            <ScheduleWidget events={events} />
            <ScheduleWidget events={tomorrowEvents} title="Tomorrow's Schedule" />
            <DecisionsWidget decisions={decisions} />
          </div>

          <div className="lg:col-span-1 flex flex-col gap-gutter">
            <InsightsWidget insight={insight} />
            <CriticalCommsWidget emails={emails} />
            <MeetingStatsWidget stats={meetingStats} />
          </div>
        </div>

        {/* Urgent Matters */}
        <div className="mb-gutter">
          <UrgentMattersWidget matters={urgentMatters} />
        </div>

        {/* Registers & Trackers */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-gutter mb-gutter">
          <RiskRegisterWidget risks={risksData} />
          <FollowUpRegisterWidget commitments={commitmentsData} />
          <BoardPaperTrackerWidget papers={boardPapersData} />
        </div>

        {/* Board Meetings */}
        <div className="mb-gutter">
          <BoardMeetingsWidget meetings={upcomingBoardMeetingsData} />
        </div>

        {/* Workload & Departments */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-gutter mb-gutter">
          <WaitingForWidget waitingForMe={waitingForMeData} waitingForOthers={waitingForOthersData} />
          <DepartmentStatusWidget report={departmentReport} />
        </div>

        {/* Recent Decisions */}
        <div>
          <DecisionsWidget decisions={recentDecisions} title="Recent Decisions" />
        </div>
      </main>
    </>
  );
}
