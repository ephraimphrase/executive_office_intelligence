# EOIS — Build History

A step-by-step record of how the Executive Office Intelligence System was
built, in the order it actually happened, plus an honest accounting of what
is *not* done yet. Written for whoever picks this project up next — a future
session, a new engineer, or the client team doing due diligence.

**Stack:** FastAPI + SQLAlchemy (async) + Celery/Redis + PostgreSQL/pgvector
on the backend; Next.js 16 (App Router) + React 19 + TypeScript + Tailwind v4
on the frontend. Source spec: `requirement doc Dangote.pdf` (a "Master
Prompt" describing EOIS as an AI Chief of Staff for a Dangote Group GVP).

---

## Phase 1 — Onboarding and orientation

Read the full codebase (backend routers/services/models, frontend pages/
components, existing tests) to build a working model of the system before
changing anything: the mock/real fallback pattern used for every external
integration (Graph, WhatsApp, OpenAI, Azure Blob — each checks
`self.enabled`/`self.use_mock` and falls back to realistic mock data when
credentials are absent), the async SQLAlchemy setup with a SQLite dev
fallback (`_is_sqlite` flag in `database.py`), and the existing test suite's
pattern of overriding `get_current_user`/`get_db` in `conftest.py`.

## Phase 2 — SSR cookie-forwarding bug

**Found:** Next.js Server Components' `fetch` calls don't automatically carry
the browser's session cookie — `credentials: "include"` only does something
in a browser context. Every page doing server-side data fetching
(dashboard, calendar, tasks, documents, communications) was silently
fetching as an unauthenticated user.

**Fixed:** added `frontend/src/lib/server-cookies.ts` (`getServerCookieHeader()`,
reads the incoming request's cookies via `next/headers` and serializes them
back into a `Cookie` header) and threaded an optional `cookieHeader` param
through every SSR-relevant function in `lib/api.ts`. Applied across all 5
affected pages.

## Phase 3 — Requirement-doc gap analysis

Read `requirement doc Dangote.pdf` page by page and diffed it against the
actual codebase to produce a concrete "what's left" list — the basis for
everything that followed.

## Phase 4 — External integrations build-out

Built out (in mock/real-fallback form, matching the existing pattern) the
integrations and features the gap analysis flagged as missing or half-built:

- **Entra ID / Microsoft SSO + local-login fallback**: `/api/auth/microsoft`,
  `/api/auth/login`, `/api/auth/refresh`, `/api/auth/logout`, `/api/auth/me`.
- **MFA (TOTP)**: `pyotp` + `qrcode`, `/api/auth/mfa/setup|enable|disable|verify`,
  backup codes, `User.mfa_enabled/mfa_secret/mfa_backup_codes`.
- **Audit logging**: new `AuditLog` model/service/router, wired into
  auth, decisions, tasks, risks, commitments, documents, users routers.
- **Microsoft Teams integration**: `TeamsMessage` model (was previously not
  a real table), `app/services/teams.py`, `/api/teams/*` router,
  `tasks/teams_polling.py` Celery task, Graph client methods
  (`list_chats`, `get_chat_messages`, `list_joined_teams`, `get_channel_messages`).
- **WhatsApp Business webhook**: `WhatsAppMessage` (was a plain dataclass,
  rebuilt as a real SQLAlchemy model), `/api/whatsapp/webhook` (GET verify +
  POST receive), stats endpoint.
- **Real vector search (pgvector)**: `Document.embedding` column
  (dialect-conditional — `pgvector.sqlalchemy.Vector` on Postgres, plain JSON
  float array on SQLite with a Python-side cosine-similarity fallback in
  `knowledge_base.py`), real file text extraction for Word/PDF/Excel/PowerPoint
  (`python-docx`, `pypdf`, `openpyxl`, `python-pptx`).
- **Azure Blob Storage**: `AzureBlobClient` (mock/real pattern), wired into
  the documents upload/delete flow with a local-disk dev fallback.
- **Backup/DR documentation**: `backend/docs/BACKUP_AND_DR.md`.

Frontend side: rewrote `login/page.tsx` (MFA challenge branching + Microsoft
SSO redirect), added `auth/callback/page.tsx` for the OAuth return leg.

## Phase 5 — External credentials research

Compiled every remaining external requirement (Azure AD tenant + app
registration, OpenAI API key, WhatsApp Business API, Azure Blob Storage,
production Postgres) into `backend/docs/EXTERNAL_SETUP_CHECKLIST.md`, with
concrete step-by-step provisioning instructions and the exact `.env` keys
each one maps to — the only thing standing between "fully mocked" and "fully
live" is filling in that document, not more code.

## Phase 6 — Final QA pass: spec reconciliation + bug sweep

Re-read the requirement doc one more time against the built system, then did
a full bug/optimization sweep. Highlights, in the order they were done:

1. **`Document.access_level`** — the frontend referenced this field; it
   didn't exist on the backend model/schema. Added
   `DocumentAccessLevel` enum + column + schema field.
2. **Shared extraction pipeline** (`app/services/extraction_pipeline.py`) —
   email, WhatsApp, and Teams ingestion each had their own copy of "turn
   AI-extracted meetings/actions/decisions/commitments/risks into real DB
   rows" logic. Centralized it into one module (`auto_create_records`,
   `apply_reschedules`, `_notify_new_risks`) and pointed all three ingestion
   paths at it.
3. **`email_processor.py` rewrite** — auto-transitions `UNREAD → PROCESSED`
   after analysis (a literal spec requirement, "Archive Processed Emails"),
   added attachment download + text extraction + indexing, added
   high-priority-email notifications, wired the shared extraction pipeline.
4. **Meeting action items → real Task rows**, and a new
   `POST /meetings/{id}/generate-decisions` endpoint that extracts decisions
   from a transcript and writes real `Decision` rows (previously only agenda/
   minutes generation existed; actions and decisions stayed as raw JSON on
   the meeting record and never became real, trackable rows).
5. **Daily briefing generator rewrite** — was hardcoding `emails: []` and
   `risks: []`; now pulls real critical/high-priority emails, real open
   CRITICAL/HIGH risks, real pending decisions, live weather, and
   AI-generated talking points + risk summary. Added
   `build_briefing_record()` to map *all* ~10 `Briefing` model fields from
   the generated pack (previously only 3 fields were ever populated, in three
   separately-duplicated places).
6. **Chat assistant given real data access** — `agents/orchestrator.py`'s
   `handle_chat` was calling the LLM with a hardcoded empty
   `context = {"today_events": [], "recent_tasks": []}`, so it could not
   answer any real question about the GVP's actual schedule, tasks, decisions,
   emails, or risks. Rewrote `_build_chat_context()` to query all of the
   above for real, plus added `_extract_search_keywords()` so a natural-
   language question ("What decisions were made on the Refinery?") gets
   turned into actual search keywords before hitting `global_search` (which
   only does ILIKE substring matching and never matches a full sentence).
   Also extended `global_search` to cover Risk/Commitment/Document (it
   previously only covered emails/tasks/decisions/events, despite
   "documents" being a valid, silently-empty filter value in the API).
7. **Word export endpoints exposed** — `WordGeneratorService.generate_action_register`/
   `generate_decision_register` existed but had no route;
   added `POST /api/reports/action-register` and `/decision-register`.
8. **Document auto-categorization** — `Document.is_board_paper/is_policy/
   is_contract` were never set automatically; added a keyword-based
   classifier (`KnowledgeBaseService._classify_document`) run during
   `sync_onedrive`.
9. **Dashboard gaps** — added Tomorrow's Schedule, Upcoming Board Meetings,
   and Meeting Statistics widgets (new `/calendar/tomorrow` endpoint,
   fixed `/calendar/upcoming-board` filter bug — see below).

### General bug sweep (same phase)

A recurring bug class kept surfacing: **filters comparing an enum-typed
column against a lowercase string literal that never matches the actual
(uppercase) enum value**, so the endpoint silently returned wrong or empty
results instead of erroring. Found and fixed across the codebase:

| Endpoint | Bug |
|---|---|
| `GET /calendar/upcoming-board` | `Event.event_type == 'board'` vs. real value `EventType.BOARD` — endpoint always returned nothing |
| `GET /emails/critical` | `'critical'`/`'unread'` vs. `EmailPriority.URGENT`/`EmailStatus.UNREAD` |
| `GET /decisions/pending` | `'pending_implementation'` vs. `DecisionStatus.PENDING_IMPLEMENTATION` |
| `GET /tasks/overdue`, `/waiting-for-me`, `/waiting-for-others` | `Task.status != 'done'` vs. `TaskStatus.DONE` — **completed tasks were never excluded from these lists** |
| `GET /commitments/overdue`, `/due-soon` | `'fulfilled'` vs. `CommitmentStatus.FULFILLED` |
| `POST /tasks/{id}/escalate` | set `priority = 'critical'` instead of `TaskPriority.CRITICAL` |
| `GET /tasks/stats` | lowercased status/priority keys, breaking the dashboard's Task Completion % widget, which reads `by_status["DONE"]` |

Plus, separately:

- **`decisions.py` list filter** referenced a nonexistent `Decision.made_by_id`
  attribute (would `AttributeError` if the `made_by` query param was ever used).
- **`audit_logs.py`** compared a UUID column against a raw query-param
  string without parsing it — the same class of bug as the earlier
  production-breaking `get_current_user` bug from Phase 4.
- **Chat history was fully broken**: `get_chat_history()` unconditionally
  returned `[]`, and `GET /chat/history`'s `response_model` didn't even match
  the shape it was supposed to return (would have 500'd the moment it
  returned real data). Rewrote the in-memory conversation store to key by
  user (one continuous assistant thread per GVP) and fixed the response
  schema.
- **`upload_document`'s form fields weren't actually being read** —
  `category`, `subcategory`, `department`, `file_type` were declared as
  plain parameters on a multipart endpoint instead of `Form(...)`, so
  FastAPI treated them as query params; every upload silently used the
  defaults (`category="GENERAL"`) regardless of what the user picked in the
  UI. Found while testing the new document-versioning endpoint and fixed in
  both places.
- **`GET /calendar/events`** had no `ORDER BY` at all — results came back in
  arbitrary/insertion order.

Every fix in this phase was verified with a purpose-written test
(write → run → confirm → delete) before moving to the next, so nothing here
is unverified.

## Phase 7 — Production-readiness re-verification

Re-ran everything from a clean slate to be certain: `py_compile` across the
whole backend, full `pytest` run, `tsc --noEmit`, `eslint`, and a from-scratch
`next build` (cleared `.next` first). This pass caught two more things:

- **ESLint errors** (3, previously unnoticed because `next build` doesn't run
  lint in this Next.js version): two unescaped JSX quote characters, and one
  `setState`-in-`useEffect` pattern flagged by a newer, stricter
  `eslint-plugin-react-hooks` rule (kept the correct, standard "fetch on
  mount" pattern and suppressed that one rule with a documented reason,
  rather than distorting working code to satisfy an overzealous linter).
  Also cleaned up ~20 trivial unused-variable/import warnings.
- **The calendar page was rendering entirely fake data** — `CalendarGrid`
  never used its `events` prop at all; it always rendered five hardcoded
  meetings under a hardcoded "October 21 – 25, 2024" header, regardless of
  what was actually in the database. Rewrote it end-to-end: added a
  `/calendar/week`-backed fetch, threaded real `start_datetime` through
  `EventItem`, and rebuilt the grid to bucket real events by actual
  weekday/hour with a real, current week header.

(One self-inflicted detour in this phase: a quick Python script meant to
strip unused `catch (error)` bindings from `lib/api.ts` had a brace-counting
bug and briefly broke six `catch` blocks that *do* use `error`. Caught
immediately by the same re-verification loop and fully repaired — mentioned
here for transparency, not because it's still a problem.)

## Phase 8 — Feature completion pass

With the codebase clean and verified, built out the remaining gaps that had
been flagged but not yet built:

- **PowerPoint generation** — new `PowerPointGeneratorService`
  (`app/services/pptx_generator.py`, using `python-pptx`, already a
  dependency for reading `.pptx` files but never used for writing them).
  Wired into `GET /briefings/{id}/export?format=pptx` (turns the Executive
  Briefing Pack into a slide deck: priorities, schedule, risks, pending
  decisions, talking points) and a new `GET /meetings/{id}/deck` endpoint
  (agenda + participants + AI talking points for a single meeting).
- **`MeetingPrepPanel` wired to real data** — previously 100% hardcoded
  (fake agenda items, fake attendee avatars, a fixed "AI insight" quote,
  fake reference documents) except for the header. Added
  `GET /calendar/events/{id}/prep` (real agenda, real attendees, AI-generated
  talking points via the existing `calendar_agent`, and related documents
  found via keyword search), and rewrote the panel to fetch and render it,
  with loading states and empty states instead of static content.
- **Document version history** — new `DocumentVersion` model + `version`
  counter on `Document`; `GET/POST /documents/{id}/versions` and
  `GET /documents/{id}/versions/{version_id}/download`. Uploading a new
  version snapshots the previous content (lazily creating a "version 1"
  snapshot on the very first new upload, for documents that predate version
  tracking) and updates the document's current content in place. Frontend:
  a `DocumentVersionModal` reachable from a history icon on each document
  card, showing the version list with download links and an upload-new-
  version action.
- **Month and Committee calendar views** — the "Week / Month / Agenda"
  segmented control in the calendar page was purely decorative (no state,
  no wiring). Extracted a shared `CalendarViewSwitcher`, built `MonthGrid`
  (a real Mon-start 6-week grid with prev/next month navigation, fetching
  the visible range via a new `GET /calendar/events?date_from=&date_to=`
  client-side call) and `CommitteeView` (upcoming/past Board + Executive
  Committee meetings, backed by a new `GET /meetings/committee` endpoint —
  org-wide, not filtered to meetings the current user created, since a
  committee calendar needs to show the whole committee's schedule). Wired
  all three views into `CalendarClient` with shared selection state.

Every item above was verified the same way as Phase 6: a real test written
against the new code, run, confirmed passing, then deleted — plus a full
`pytest` + `tsc` + `eslint` + `next build` pass at the end of the phase.

---

## Current state

- **Backend**: 34/34 tests passing, `py_compile` clean across `app/`,
  `agents/`, `tasks/`.
- **Frontend**: `tsc --noEmit` clean, `eslint` clean (0 errors — 2 harmless
  `<img>`-vs-`next/image` performance suggestions remain, deliberately left
  since switching them carries visual-regression risk without a browser to
  check them in), fresh `next build` succeeds.
- Every external integration (Graph/Teams/WhatsApp/OpenAI/Azure Blob) works
  right now against realistic mock data and is coded to switch to real
  behavior the moment credentials are supplied — no further code changes
  needed for that switch.

## What's NOT done

**Gated on external setup, not code** (see
`backend/docs/EXTERNAL_SETUP_CHECKLIST.md` for exact steps):
- Entra ID (Azure AD) tenant + app registration — needed for real SSO and
  real (non-mock) Graph email/calendar/OneDrive/Teams access.
- WhatsApp Business API credentials.
- OpenAI API key (or Azure OpenAI) — the single highest-leverage item; every
  AI feature currently runs against a deterministic mock.
- Azure Blob Storage connection string.
- A real Postgres instance with the `pgvector` extension for production
  (dev currently runs on SQLite with a Python-side cosine-similarity
  fallback).

**Not built, and not gated on credentials** — genuine remaining gaps:
- **Yearly calendar view** — Week/Month/Committee exist; a year-at-a-glance
  view does not.
- **`MeetingPrepPanel`'s "Join Virtual Room" button** is still a static,
  non-functional button — no real video-conferencing integration.
- **Document "Summarize" button** on the documents page
  (`POST /documents/{id}/summarize`) still returns a hardcoded placeholder
  string rather than a real regenerated AI summary.
- **End-to-end encryption at rest** is not implemented at the application
  layer — this relies on the underlying cloud provider's (Azure/AWS/etc.)
  storage-level encryption once deployed there, which is standard practice
  but worth being explicit about.
- **The specification's aspirational "9 specialized agents" breakdown** is
  realized as 5 in practice (base, briefing, calendar, chat, email/task
  agents). The requirement doc itself frames the 9-agent split as "an idea,"
  not a hard requirement, so this was deliberately deprioritized rather than
  overlooked.
- **Real-time collaborative presence** (e.g., seeing who else is viewing a
  document/meeting live) doesn't exist. Notifications do have a real SSE
  stream (`GET /notifications/stream`), but there's no broader
  presence/collaboration layer.

Nothing in the second list is a crash risk or a silent-wrong-answer risk —
they're scoped-out features, not defects. Everything in the bug sweep
sections above, by contrast, was a real defect and has been fixed and
verified.
