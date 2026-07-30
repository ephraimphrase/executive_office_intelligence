const API_BASE_URL = "http://localhost:8000/api";

// When called from a Server Component (SSR), `fetch` runs on the Next.js
// server and has no browser to attach the visitor's session cookie for —
// `credentials: "include"` only does something in a browser context. Server
// Components that need authenticated data must read the incoming request's
// cookies themselves (see lib/server-cookies.ts) and pass the header string
// through here so it can be forwarded explicitly.
async function apiFetch(input: RequestInfo | URL, init?: RequestInit, cookieHeader?: string): Promise<Response> {
  const options = init || {};
  options.credentials = "include"; // Send cookies (HTTP-only JWT) when running in the browser

  if (cookieHeader) {
    options.headers = { ...(options.headers || {}), Cookie: cookieHeader };
  }

  const response = await fetch(input, options);

  if (response.status === 401) {
    // If we get a 401, we should probably trigger a logout or redirect
    // But since this is a library file, throwing or relying on Context is tricky
    // We can just redirect to login if we are in the browser
    if (typeof window !== "undefined" && window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
  }

  return response;
}


// --- Types (Matching Backend Schema) ---

export interface Task {
  id: string;
  title: string;
  description: string;
  due_date: string | null;
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  status: "TODO" | "IN_PROGRESS" | "WAITING" | "DONE" | "OVERDUE" | "CANCELLED";
  department: string | null;
}

export interface Event {
  id: string;
  title: string;
  start_datetime: string;
  end_datetime: string;
  location: string | null;
  event_type: "MEETING" | "BOARD" | "TRAVEL" | "SITE_VISIT" | "CALL" | "PERSONAL" | "OTHER";
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
}

export interface Decision {
  id: string;
  title: string;
  description: string;
  status: "PENDING" | "APPROVED" | "REJECTED" | "DEFERRED";
  priority: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  due_date: string | null;
}

export interface Email {
  id: string;
  subject: string;
  sender_name: string;
  received_at: string;
  priority: "URGENT" | "HIGH" | "NORMAL" | "LOW";
  status: "UNREAD" | "READ" | "PROCESSED" | "ARCHIVED" | "REPLIED";
}

export interface Document {
  id: string;
  title: string;
  category: "BOARD" | "FINANCIAL" | "BRIEFING";
  last_modified: string;
  access_level: string;
  type: "PDF" | "EXCEL" | "WORD" | "OTHER";
}

export interface Risk {
  id: string;
  description: string;
  category: string | null;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  status: "OPEN" | "MITIGATED" | "CLOSED" | "ACCEPTED";
  owner: string | null;
  department: string | null;
  deadline: string | null;
}

export interface Commitment {
  id: string;
  description: string;
  owner: string | null;
  status: "PENDING" | "IN_PROGRESS" | "FULFILLED" | "OVERDUE" | "CANCELLED";
  deadline: string | null;
  department: string | null;
}

export interface WaitingTask {
  id: string;
  title: string;
  status: string;
  priority: string;
  due_date: string | null;
}

export interface TaskStats {
  total: number;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
}

export interface DecisionStats {
  total: number;
  implemented: number;
  pending: number;
  by_department: Record<string, number>;
}

export interface EmailStats {
  total_count: number;
  critical_count: number;
  high_count: number;
  unread_count: number;
  response_rate: string;
}

export interface DepartmentTaskReport {
  [department: string]: { total: number; completed: number; overdue: number };
}

export interface MeetingStats {
  total_meetings: number;
  period: { from: string; to: string };
}

export interface Meeting {
  id: string;
  title: string;
  meeting_date: string;
  start_time: string | null;
  end_time: string | null;
  location: string | null;
  meeting_type: "BOARD" | "EXECUTIVE_COMMITTEE" | "DEPARTMENT" | "ONE_ON_ONE" | "EXTERNAL" | "SITE_VISIT";
  chairperson: string | null;
  status: "SCHEDULED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";
  board_paper_required: boolean;
  board_paper_submitted: boolean;
}

export async function fetchCommitteeMeetings(): Promise<Meeting[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/meetings/committee`);
    if (res.ok) return (await res.json()) as Meeting[];
  } catch {
    console.warn("Backend offline. Using empty committee meetings.");
  }
  return [];
}

// --- Fetch Wrappers with Fallback Mock Data ---
// We use fallback mocks in case the backend is currently not running locally

export async function fetchEvents(cookieHeader?: string): Promise<Event[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/calendar/events?limit=5`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as Event[];
  } catch {
    console.warn("Backend offline. Using mock Events.");
  }
  return [
    {
      id: "1",
      title: "Board Strategy Session",
      start_datetime: new Date(new Date().setHours(9, 0, 0, 0)).toISOString(),
      end_datetime: new Date(new Date().setHours(11, 0, 0, 0)).toISOString(),
      location: "Conference Room A",
      event_type: "BOARD",
      priority: "CRITICAL",
    },
    {
      id: "2",
      title: "Q3 Financial Review",
      start_datetime: new Date(new Date().setHours(13, 0, 0, 0)).toISOString(),
      end_datetime: new Date(new Date().setHours(14, 30, 0, 0)).toISOString(),
      location: "Virtual",
      event_type: "MEETING",
      priority: "HIGH",
    },
    {
      id: "3",
      title: "1:1 with VP Engineering",
      start_datetime: new Date(new Date().setHours(15, 0, 0, 0)).toISOString(),
      end_datetime: new Date(new Date().setHours(16, 0, 0, 0)).toISOString(),
      location: "GVP Office",
      event_type: "MEETING",
      priority: "MEDIUM",
    },
  ];
}

export async function fetchWeekEvents(cookieHeader?: string): Promise<Event[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/calendar/week`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as Event[];
  } catch {
    console.warn("Backend offline. Using mock Week Events.");
  }
  return [];
}

export async function fetchEventsInRange(dateFrom: string, dateTo: string): Promise<Event[]> {
  try {
    const res = await apiFetch(
      `${API_BASE_URL}/calendar/events?date_from=${encodeURIComponent(dateFrom)}&date_to=${encodeURIComponent(dateTo)}`
    );
    if (res.ok) return (await res.json()) as Event[];
  } catch {
    console.warn("Backend offline. Using empty event range.");
  }
  return [];
}

export async function fetchTomorrowEvents(cookieHeader?: string): Promise<Event[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/calendar/tomorrow`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as Event[];
  } catch {
    console.warn("Backend offline. Using mock Tomorrow's Events.");
  }
  return [];
}

export async function fetchUpcomingBoardMeetings(cookieHeader?: string): Promise<Event[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/calendar/upcoming-board`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as Event[];
  } catch {
    console.warn("Backend offline. Using mock Upcoming Board Meetings.");
  }
  return [];
}

export async function fetchMeetingStats(cookieHeader?: string): Promise<MeetingStats> {
  try {
    const today = new Date();
    const start = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().slice(0, 10);
    const end = today.toISOString().slice(0, 10);
    const res = await apiFetch(
      `${API_BASE_URL}/reports/meeting-statistics?start_date=${start}&end_date=${end}`,
      undefined,
      cookieHeader
    );
    if (res.ok) return (await res.json()) as MeetingStats;
  } catch {
    console.warn("Backend offline. Using mock Meeting Stats.");
  }
  return { total_meetings: 0, period: { from: "", to: "" } };
}

export interface EventPrep {
  event_id: string;
  title: string;
  agenda: string[];
  attendees: string[];
  talking_points: string[];
  documents: SearchResult[];
}

export async function fetchEventPrep(eventId: string): Promise<EventPrep | null> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/calendar/events/${eventId}/prep`);
    if (res.ok) return (await res.json()) as EventPrep;
  } catch {
    console.warn("Backend offline. Could not load meeting prep.");
  }
  return null;
}

export async function createEvent(eventData: Omit<Event, "id">): Promise<Event> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/calendar/events`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(eventData),
    });
    if (res.ok) {
      return (await res.json()) as Event;
    }
    throw new Error(`Failed to create event: ${res.statusText}`);
  } catch (error) {
    console.error("Error creating event:", error);
    throw error;
  }
}

export async function fetchDecisions(cookieHeader?: string): Promise<Decision[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/decisions?status=PENDING&limit=5`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as Decision[];
  } catch {
    console.warn("Backend offline. Using mock Decisions.");
  }
  return [
    {
      id: "1",
      title: "Q3 Budget Approval - Asia-Pac",
      description: "Final sign-off for regional marketing spend.",
      status: "PENDING",
      priority: "HIGH",
      due_date: new Date(new Date().setDate(new Date().getDate() + 1)).toISOString(),
    },
    {
      id: "2",
      title: "New Head of Sales Candidate",
      description: "Final interview feedback and offer approval.",
      status: "PENDING",
      priority: "CRITICAL",
      due_date: null,
    },
  ];
}

export async function fetchEmails(cookieHeader?: string): Promise<Email[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/emails?limit=10`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as Email[];
  } catch {
    console.warn("Backend offline. Using mock Emails.");
  }

  // Fallback Mock Data
  return [
    {
      id: "1",
      subject: "Draft Q4 Strategic Pivot - Confidential",
      sender_name: "Project Titan Steering",
      received_at: new Date().toISOString(),
      priority: "URGENT",
      status: "UNREAD"
    },
    {
      id: "2",
      subject: "Urgent: Budget Approval Needed",
      sender_name: "Julian V. (CFO)",
      received_at: new Date(Date.now() - 14 * 60000).toISOString(),
      priority: "HIGH",
      status: "UNREAD"
    }
  ];
}

export async function fetchDocuments(cookieHeader?: string): Promise<Document[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/documents?limit=10`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as Document[];
  } catch {
    console.warn("Backend offline. Using mock Documents.");
  }

  // Fallback Mock Data
  return [
    {
      id: "1",
      title: "Q3 Strategic Growth Initiative",
      category: "BOARD",
      last_modified: "2023-10-24T00:00:00Z",
      access_level: "Confidential",
      type: "PDF"
    },
    {
      id: "2",
      title: "Minutes of Governance Board",
      category: "BOARD",
      last_modified: "2023-10-22T00:00:00Z",
      access_level: "Internal Only",
      type: "WORD"
    },
    {
      id: "3",
      title: "Global Market Expansion v2.4",
      category: "BOARD",
      last_modified: "2023-10-20T00:00:00Z",
      access_level: "Restricted",
      type: "PDF"
    },
    {
      id: "4",
      title: "Annual Profitability Forecast",
      category: "FINANCIAL",
      last_modified: "2023-10-25T00:00:00Z",
      access_level: "Live Data",
      type: "EXCEL"
    },
    {
      id: "5",
      title: "OPEX Analysis - Regional",
      category: "FINANCIAL",
      last_modified: "2023-10-19T00:00:00Z",
      access_level: "Public Release",
      type: "EXCEL"
    },
    {
      id: "6",
      title: "Executive Summary: AI Ethics",
      category: "BRIEFING",
      last_modified: "2023-10-24T00:00:00Z",
      access_level: "Briefing",
      type: "WORD"
    }
  ];
}

// --- Risk Register ---

export async function fetchOpenRisks(cookieHeader?: string): Promise<Risk[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/risks/open`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as Risk[];
  } catch {
    console.warn("Backend offline. Using mock Risks.");
  }
  return [
    {
      id: "1",
      description: "Supply chain disruption in Southeast Asia may impact Q3 targets.",
      category: "Operations",
      severity: "HIGH",
      status: "OPEN",
      owner: "Ops Lead",
      department: "Electronics",
      deadline: null,
    },
  ];
}

// --- Follow-up Register (Commitments) ---

export async function fetchCommitmentsDueSoon(cookieHeader?: string): Promise<Commitment[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/commitments/due-soon`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as Commitment[];
  } catch {
    console.warn("Backend offline. Using mock Commitments.");
  }
  return [
    {
      id: "1",
      description: "Send revised budget to CFO",
      owner: "GVP Office",
      status: "PENDING",
      deadline: new Date(new Date().setDate(new Date().getDate() + 2)).toISOString(),
      department: "Finance",
    },
  ];
}

// --- Board Paper Tracker ---

export async function fetchBoardPapers(cookieHeader?: string): Promise<Document[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/documents/board-papers`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as Document[];
  } catch {
    console.warn("Backend offline. Using mock Board Papers.");
  }
  return [
    {
      id: "1",
      title: "Q3 Strategic Growth Initiative",
      category: "BOARD",
      last_modified: "2023-10-24T00:00:00Z",
      access_level: "Confidential",
      type: "PDF",
    },
  ];
}

// --- Waiting For Me / Waiting For Others ---

export async function fetchWaitingForMe(cookieHeader?: string): Promise<WaitingTask[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/tasks/waiting-for-me`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as WaitingTask[];
  } catch {
    console.warn("Backend offline. Using mock Waiting-For-Me tasks.");
  }
  return [];
}

export async function fetchOverdueTasks(cookieHeader?: string): Promise<WaitingTask[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/tasks/overdue`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as WaitingTask[];
  } catch {
    console.warn("Backend offline. Using mock Overdue Tasks.");
  }
  return [];
}

export async function fetchWaitingForOthers(cookieHeader?: string): Promise<WaitingTask[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/tasks/waiting-for-others`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as WaitingTask[];
  } catch {
    console.warn("Backend offline. Using mock Waiting-For-Others tasks.");
  }
  return [];
}

// --- Executive KPIs / Stats ---

export async function fetchTaskStats(cookieHeader?: string): Promise<TaskStats> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/tasks/stats`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as TaskStats;
  } catch {
    console.warn("Backend offline. Using mock Task Stats.");
  }
  return { total: 0, by_status: {}, by_priority: {} };
}

export async function fetchDecisionStats(cookieHeader?: string): Promise<DecisionStats> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/decisions/stats`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as DecisionStats;
  } catch {
    console.warn("Backend offline. Using mock Decision Stats.");
  }
  return { total: 0, implemented: 0, pending: 0, by_department: {} };
}

export async function fetchEmailStats(cookieHeader?: string): Promise<EmailStats> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/emails/stats`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as EmailStats;
  } catch {
    console.warn("Backend offline. Using mock Email Stats.");
  }
  return { total_count: 0, critical_count: 0, high_count: 0, unread_count: 0, response_rate: "0%" };
}

export async function fetchDepartmentTaskReport(cookieHeader?: string): Promise<DepartmentTaskReport> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/reports/task-completion`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as DepartmentTaskReport;
  } catch {
    console.warn("Backend offline. Using mock Department Report.");
  }
  return {};
}

export async function fetchRecentDecisions(cookieHeader?: string): Promise<Decision[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/decisions?limit=5`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as Decision[];
  } catch {
    console.warn("Backend offline. Using mock Recent Decisions.");
  }
  return [];
}

export async function uploadDocument(file: File, category: string, subcategory: string): Promise<Document> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("category", category);
  formData.append("subcategory", subcategory);

  try {
    const res = await apiFetch(`${API_BASE_URL}/documents/upload`, {
      method: "POST",
      // Include authorization headers if necessary
      // headers: { "Authorization": `Bearer ${token}` },
      body: formData,
    });
    
    if (res.ok) {
      return (await res.json()) as Document;
    }
    throw new Error(`Upload failed: ${res.statusText}`);
  } catch (error) {
    console.error("Error uploading document:", error);
    throw error;
  }
}

export interface DocumentVersion {
  id: string;
  document_id: string;
  version_number: number;
  name: string;
  size_bytes: number | null;
  change_note: string | null;
  uploaded_by_id: string | null;
  created_at: string;
}

export async function fetchDocumentVersions(docId: string): Promise<DocumentVersion[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/documents/${docId}/versions`);
    if (res.ok) return (await res.json()) as DocumentVersion[];
  } catch {
    console.warn("Backend offline. Using empty version history.");
  }
  return [];
}

export async function uploadDocumentVersion(docId: string, file: File, changeNote?: string): Promise<DocumentVersion> {
  const formData = new FormData();
  formData.append("file", file);
  if (changeNote) formData.append("change_note", changeNote);

  const res = await apiFetch(`${API_BASE_URL}/documents/${docId}/versions`, {
    method: "POST",
    body: formData,
  });
  if (res.ok) return (await res.json()) as DocumentVersion;
  throw new Error(`Failed to upload new version: ${res.statusText}`);
}

export function getDocumentVersionDownloadUrl(docId: string, versionId: string): string {
  return `${API_BASE_URL}/documents/${docId}/versions/${versionId}/download`;
}

export interface SearchResult {
  id: string;
  type: "email" | "document" | "decision" | "event" | "task";
  title: string;
  snippet?: string;
  url?: string;
}

export async function searchAll(query: string, type: string = "all"): Promise<SearchResult[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/search?q=${encodeURIComponent(query)}&type=${type}`);
    if (res.ok) return await res.json();
  } catch {
    console.warn("Backend offline. Using mock SearchResults.");
  }
  return [];
}

export async function searchSuggestions(query: string): Promise<string[]> {
  if (query.length < 2) return [];
  try {
    const res = await apiFetch(`${API_BASE_URL}/search/suggestions?q=${encodeURIComponent(query)}`);
    if (res.ok) return await res.json();
  } catch {
    // Ignore error
  }
  return [];
}

export async function fetchTasks(cookieHeader?: string): Promise<Task[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/tasks?status=TODO&limit=10`, undefined, cookieHeader);
    if (res.ok) return (await res.json()) as Task[];
  } catch {
    console.warn("Backend offline. Using mock Tasks.");
  }
  // Returning 12 total tasks based on the UI mockup metric count
  return Array.from({ length: 12 }).map((_, i) => ({
    id: String(i),
    title: `Task ${i}`,
    description: "Sample Task",
    due_date: null,
    priority: "MEDIUM",
    status: "TODO",
    department: null,
  }));
}

export async function createTask(taskData: Omit<Task, "id">): Promise<Task> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(taskData),
    });
    if (res.ok) return await res.json();
    throw new Error(`Failed to create task: ${res.statusText}`);
  } catch (error) {
    console.error("Error creating task:", error);
    throw error;
  }
}

export async function updateTask(taskId: string, updateData: Partial<Task>): Promise<Task> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/tasks/${taskId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updateData),
    });
    if (res.ok) return await res.json();
    throw new Error(`Failed to update task: ${res.statusText}`);
  } catch (error) {
    console.error("Error updating task:", error);
    throw error;
  }
}

// --- AI Chat ---

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export async function sendChatMessage(
  message: string,
  conversationId?: string
): Promise<{ response: string; conversation_id?: string }> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/chat/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
    if (res.ok) {
      const data = await res.json();
      return { response: data.reply, conversation_id: data.conversation_id };
    }
    throw new Error(`Chat error: ${res.statusText}`);
  } catch (error) {
    console.error("Error sending chat message:", error);
    // Graceful mock fallback when backend is offline
    return {
      response:
        "I'm currently operating in offline mode. The backend AI service is unavailable. Please ensure the EOIS backend is running on port 8000.",
    };
  }
}

export async function fetchChatHistory(): Promise<ChatMessage[]> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/chat/history?limit=50`);
    if (res.ok) return await res.json();
  } catch {
    // offline
  }
  return [];
}

// --- Communications (Email Reply) ---

export async function sendEmailReply(
  emailId: string,
  replyBody: string
): Promise<{ success: boolean; message: string }> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/emails/${emailId}/reply`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ body: replyBody }),
    });
    if (res.ok) return { success: true, message: "Reply sent successfully." };
    throw new Error(res.statusText);
  } catch (error) {
    console.error("Error sending reply:", error);
    return { success: false, message: "Failed to send reply. Backend may be offline." };
  }
}

// --- Auth: MFA + Microsoft SSO ---

export async function verifyMfaCode(
  challengeToken: string,
  code: string
): Promise<{ ok: boolean; message?: string }> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/auth/mfa/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ challenge_token: challengeToken, code }),
    });
    if (res.ok) return { ok: true };
    const data = await res.json().catch(() => ({}));
    return { ok: false, message: data.detail || "Invalid authentication code" };
  } catch {
    return { ok: false, message: "Failed to connect to the server. Please try again." };
  }
}

export async function exchangeMicrosoftCode(
  code: string,
  redirectUri: string
): Promise<{ ok: boolean; message?: string }> {
  try {
    const res = await apiFetch(`${API_BASE_URL}/auth/microsoft`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, redirect_uri: redirectUri }),
    });
    if (res.ok) return { ok: true };
    const data = await res.json().catch(() => ({}));
    return { ok: false, message: data.detail || "Could not complete Microsoft sign-in" };
  } catch {
    return { ok: false, message: "Failed to connect to the server. Please try again." };
  }
}

export async function updateEmailStatus(emailId: string, status: "READ" | "UNREAD" | "PROCESSED" | "ARCHIVED" | "REPLIED"): Promise<void> {
  try {
    await apiFetch(`${API_BASE_URL}/emails/${emailId}/status`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status }),
    });
  } catch {
    // non-critical
  }
}
