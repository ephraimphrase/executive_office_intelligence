# Executive Office Intelligence System (EOIS)

An AI-powered "Chief of Staff" application built for the Group Vice President
(GVP) of Dangote Group. EOIS ingests the GVP's email, calendar, Teams,
WhatsApp, and documents, uses an LLM to extract meetings, tasks, decisions,
commitments, and risks from that raw traffic, and surfaces it all through a
dashboard, AI chat assistant, and generated daily briefings — so the exec
office spends less time triaging inputs and more time on decisions.

Built from a client specification document (`requirement doc Dangote.pdf`,
a "Master Prompt" describing the desired system). See `BUILD_HISTORY.md` for
a full, honest, phase-by-phase account of how this was built, every bug
found and fixed along the way, and exactly what is/isn't done.

## Table of contents

- [Architecture](#architecture)
- [Repository layout](#repository-layout)
- [Features](#features)
- [How the mock/real integration pattern works](#how-the-mockreal-integration-pattern-works)
- [Prerequisites](#prerequisites)
- [Running it — fastest path (Docker)](#running-it--fastest-path-docker)
- [Running it — manual / local dev](#running-it--manual--local-dev)
- [Environment variables](#environment-variables)
- [Running tests and checks](#running-tests-and-checks)
- [API documentation](#api-documentation)
- [Going from mock to real integrations](#going-from-mock-to-real-integrations)
- [Current status / known gaps](#current-status--known-gaps)

## Architecture

```
                        ┌─────────────────────┐
                        │   Next.js frontend   │  (App Router, React 19, TS, Tailwind v4)
                        │   frontend/          │  http://localhost:3000
                        └──────────┬───────────┘
                                   │ REST (cookies)
                        ┌──────────▼───────────┐
                        │   FastAPI backend     │  http://localhost:8000
                        │   backend/app/        │  /docs (Swagger), /redoc
                        └──┬───────────┬────────┘
                           │           │
                 ┌─────────▼──┐   ┌────▼─────────┐
                 │ PostgreSQL │   │ Redis         │
                 │ + pgvector │   │ (cache/broker)│
                 └────────────┘   └───┬───────────┘
                                      │
                          ┌───────────▼────────────┐
                          │ Celery worker + beat    │  backend/tasks/
                          │ (email/calendar/Teams   │
                          │  polling, briefings,    │
                          │  notifications)         │
                          └───────────┬─────────────┘
                                      │
                     ┌────────────────┼─────────────────────┐
                     │                │                      │
             ┌───────▼──────┐  ┌──────▼───────┐   ┌──────────▼─────────┐
             │ Microsoft     │  │ OpenAI        │   │ WhatsApp Business /│
             │ Graph (Email, │  │ (extraction,  │   │ Azure Blob /        │
             │ Calendar,     │  │ chat, embed-  │   │ Azure AI Search /   │
             │ OneDrive,     │  │ dings)        │   │ OpenWeatherMap      │
             │ Teams)        │  │               │   │                     │
             └───────────────┘  └───────────────┘   └─────────────────────┘
```

- **Backend**: FastAPI (async) + SQLAlchemy (async ORM) + PostgreSQL with the
  `pgvector` extension for semantic search (SQLite fallback for local dev,
  with a Python-side cosine-similarity fallback for vector search). Celery +
  Redis run background jobs (polling inboxes/calendars/Teams, generating the
  daily briefing, sending reminders/notifications). A small set of AI
  "agents" (`backend/agents/`) wrap OpenAI calls for chat, briefings,
  calendar prep, and email/task extraction.
- **Frontend**: Next.js 16 (App Router) + React 19 + TypeScript + Tailwind v4.
  Server Components fetch data server-side (forwarding the session cookie
  manually, since SSR `fetch` doesn't do this automatically — see
  `frontend/src/lib/server-cookies.ts`); interactive pages are client
  components that call the same REST API from the browser.
- **Every external integration** (Microsoft Graph, OpenAI, WhatsApp, Azure
  Blob, Azure AI Search, OpenWeatherMap) is built with a **mock/real
  fallback pattern**: each integration client checks whether its credentials
  are configured and transparently falls back to realistic mock data if not.
  This means the whole system runs and is fully clickable/testable with zero
  external credentials — see below.

## Repository layout

```
.
├── backend/                      FastAPI application
│   ├── app/
│   │   ├── main.py                App entry point, middleware, router registration
│   │   ├── config.py              Settings (pydantic-settings, reads .env)
│   │   ├── database.py            Async SQLAlchemy engine/session, Postgres/SQLite handling
│   │   ├── models/                SQLAlchemy models (User, Email, Event, Task, Document, ...)
│   │   ├── schemas/                Pydantic request/response schemas
│   │   ├── routers/                FastAPI route handlers, one file per domain area
│   │   ├── services/                Business logic (email processing, briefing generation, ...)
│   │   ├── integrations/            External API clients (Graph, OpenAI, WhatsApp, Azure Blob/Search, weather)
│   │   └── utils/
│   ├── agents/                     LLM "agent" wrappers (chat, briefing, calendar, email/task, orchestrator)
│   ├── tasks/                      Celery task definitions (polling, briefing, notifications)
│   ├── tests/                      pytest suite
│   ├── alembic/                    Migration scaffolding (tables are currently created via
│   │                               SQLAlchemy metadata.create_all() at startup, not migrations)
│   ├── docs/
│   │   ├── BACKUP_AND_DR.md         Backup / disaster-recovery notes
│   │   └── EXTERNAL_SETUP_CHECKLIST.md  Step-by-step guide to provisioning every external credential
│   ├── docker-compose.yml          Full stack: api, worker, beat, db (pgvector), redis, flower
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example                Template — copy to .env
│   └── celery_app.py                Celery app + beat schedule
│
├── frontend/                       Next.js application
│   └── src/
│       ├── app/                     Routes (dashboard, calendar, tasks, documents, communications,
│       │                            ai-assistant, notifications, settings, login, auth/callback)
│       ├── components/              UI components, grouped by feature area
│       ├── context/                 AuthContext (session state)
│       └── lib/                     api.ts (REST client), server-cookies.ts (SSR cookie forwarding)
│
├── requirement doc Dangote.pdf      Original client specification ("Master Prompt")
├── BUILD_HISTORY.md                 Full build log: what was built, in what order, bugs found/fixed, what's left
└── README.md                        This file
```

## Features

- **Dashboard** — daily overview: today's schedule, urgent matters, waiting-for
  register, task completion, board papers, department status, risk register,
  decisions, critical comms, AI insights, tomorrow's schedule, upcoming board
  meetings, meeting statistics.
- **Calendar** — Week / Month / Committee views (year view not yet built),
  meeting prep panel with AI-generated talking points and related documents,
  agenda/minutes/decision/deck generation for meetings.
- **Communications** — unified inbox across email, Microsoft Teams, and
  WhatsApp, with AI extraction of meetings/tasks/decisions/commitments/risks
  from message content, auto-archiving processed emails, and high-priority
  notifications.
- **Tasks** — Kanban board, overdue/waiting-for-me/waiting-for-others views,
  escalation.
- **Documents** — repository with categorization (board papers / policies /
  contracts, auto-classified), version history, upload/download, and
  semantic (vector) search over content.
- **Decisions, Commitments, Risks** — trackable records auto-created from
  email/Teams/WhatsApp extraction or created manually, each with their own
  list/detail views and status workflows.
- **Daily briefing** — auto-generated each morning (real critical emails,
  open high/critical risks, pending decisions, live weather, AI talking
  points), exportable as Word or PowerPoint.
- **AI chat assistant** — natural-language Q&A grounded in the GVP's actual
  schedule, tasks, decisions, emails, and risks (not a generic chatbot).
- **Reports** — Word-exported action register and decision register.
- **Auth** — Microsoft Entra ID (Azure AD) SSO with a local-login fallback,
  TOTP-based MFA with backup codes, refresh tokens, full audit logging.
- **Notifications** — real-time via Server-Sent Events (`/notifications/stream`).

## How the mock/real integration pattern works

Every integration client (`backend/app/integrations/*.py`) checks at
startup whether the relevant credentials are present in `.env`. If they are,
it makes real API calls; if not, it returns realistic, deterministic mock
data instead of erroring. This is why **the entire application is fully
usable out of the box with no external accounts** — you'll see believable
emails, calendar events, Teams messages, WhatsApp messages, AI-generated
text, and search results, all synthetic. Supplying real credentials for any
one integration switches only that integration to live data — no code
changes required.

## Prerequisites

- **Docker & Docker Compose** (recommended path), **or**
- **Python 3.11+** and **Node.js 20+** for a fully manual setup
- No external API keys are required to run and use the app in mock mode.

## Running it — fastest path (Docker)

```bash
cd backend
cp .env.example .env
docker-compose up -d
```

This starts:
- `api` — FastAPI backend on **http://localhost:8000**
- `worker` — Celery worker (background jobs)
- `beat` — Celery beat (schedules polling/briefing jobs)
- `db` — PostgreSQL 16 with `pgvector` on port 5432
- `redis` — Redis on port 6379
- `flower` — Celery monitoring UI on **http://localhost:5555**

Then, in a separate terminal, start the frontend (not containerized in this
setup):

```bash
cd frontend
npm install
npm run dev
```

Frontend: **http://localhost:3000**. Backend API docs: **http://localhost:8000/docs**.

## Running it — manual / local dev

### Backend

```bash
cd backend
cp .env.example .env
python3 -m venv env
source env/bin/activate        # Windows: env\Scripts\activate
pip install -r requirements.txt
```

For local dev without Docker/Postgres, the simplest option is to point the
database at SQLite (the code has an explicit SQLite fallback path):

```bash
# in backend/.env
DATABASE_URL=sqlite+aiosqlite:///./eois_dev.db
DATABASE_URL_SYNC=sqlite:///./eois_dev.db
```

Otherwise, start Postgres + Redis via Docker and keep the Postgres URLs from
`.env.example`:

```bash
docker-compose up -d db redis
```

Then start the API (tables are created automatically at startup via
SQLAlchemy `create_tables()` — no separate migration step is required in
dev):

```bash
uvicorn app.main:app --reload
```

In separate terminals, start the Celery worker and beat scheduler if you
want background polling/briefing jobs to run (optional for just browsing
the UI):

```bash
celery -A celery_app worker --loglevel=info
celery -A celery_app beat --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**. Note: the API base URL is currently
hardcoded to `http://localhost:8000/api` in `frontend/src/lib/api.ts` — no
frontend `.env` is required for local dev, but this must be changed before
deploying to a real domain.

## Environment variables

All backend configuration lives in `backend/.env` (copy from
`backend/.env.example`). Everything not related to core app/DB/Redis config
is optional — the app falls back to mock data if unset. Full picture:

| Area | Variables | Required for |
|---|---|---|
| Core app | `APP_NAME`, `APP_ENV`, `DEBUG`, `SECRET_KEY`, `ALLOWED_ORIGINS` | Always |
| Database | `DATABASE_URL`, `DATABASE_URL_SYNC` | Always (Postgres or SQLite) |
| Redis / Celery | `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | Background jobs |
| Microsoft Graph | `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`, `AZURE_AUTHORITY` | Real SSO, email/calendar/OneDrive/Teams sync |
| OpenAI | `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_EMBEDDING_MODEL` | Real AI extraction/chat/briefings/embeddings |
| Azure AI Search | `AZURE_SEARCH_ENDPOINT`, `AZURE_SEARCH_KEY`, `AZURE_SEARCH_INDEX` | Real hosted vector search (optional — pgvector/SQLite fallback works without it) |
| Azure Blob Storage | `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_STORAGE_CONTAINER` | Durable document storage (falls back to local disk) |
| WhatsApp Business | `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_API_VERSION` | Real WhatsApp webhook |
| Weather | `OPENWEATHER_API_KEY`, `GVP_LOCATION_LAT/LON/NAME` | Real weather in daily briefing |
| Briefing schedule | `BRIEFING_GENERATION_HOUR/MINUTE`, `BRIEFING_TIMEZONE` | Daily briefing timing |
| JWT | `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` | Auth |
| Polling intervals | `EMAIL_POLL_INTERVAL_SECONDS`, `CALENDAR_SYNC_INTERVAL_SECONDS`, `ONEDRIVE_SYNC_INTERVAL_SECONDS` | Background sync cadence |
| GVP identity | `GVP_EMAIL`, `GVP_NAME`, `GVP_TIMEZONE` | Resolves which `User` row automation writes to |

See `backend/docs/EXTERNAL_SETUP_CHECKLIST.md` for exact step-by-step
provisioning instructions for every credential above (Azure AD app
registration, OpenAI billing/key, Postgres+pgvector on Azure, Blob Storage,
WhatsApp Business API, production Redis).

## Running tests and checks

Backend:
```bash
cd backend
source env/bin/activate
pytest                      # full test suite
python -m py_compile $(find app agents tasks -name '*.py')   # syntax/import sanity check
```

Frontend:
```bash
cd frontend
npx tsc --noEmit             # type-check
npm run lint                 # ESLint
npm run build                 # production build
```

## API documentation

With the backend running:
- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**
- Health check (shows which integrations are live vs. mocked):
  **http://localhost:8000/health**

## Going from mock to real integrations

Nothing here requires new code — only credentials. Follow
`backend/docs/EXTERNAL_SETUP_CHECKLIST.md`, which covers, in order of
leverage:

1. **OpenAI API key** — the single highest-impact item; every AI feature
   (extraction, chat, briefings, embeddings) currently runs on a
   deterministic mock.
2. **Azure AD (Entra ID) app registration** — real SSO + real Graph
   email/calendar/OneDrive/Teams access.
3. **Production PostgreSQL with the `pgvector` extension** — for real
   semantic search at scale (dev already works fine on SQLite).
4. **Azure Blob Storage** — durable document storage.
5. **WhatsApp Business Platform credentials**.
6. **Production Redis**.
7. Deployment basics: real domain + TLS, a real `SECRET_KEY`
   (`openssl rand -hex 32`), and updating `ALLOWED_ORIGINS` /
   `frontend/src/lib/api.ts`'s hardcoded `localhost:8000`.

## Current status / known gaps

As of the last verification pass (see `BUILD_HISTORY.md` for detail):
- Backend: all tests passing, clean `py_compile` across `app/`, `agents/`, `tasks/`.
- Frontend: clean `tsc --noEmit`, clean `eslint`, successful `next build`.

Not yet built, independent of credentials:
- Yearly calendar view (Week/Month/Committee exist).
- Video-conferencing integration ("Join Virtual Room" is a static button).
- Real regenerated AI document summaries (`/documents/{id}/summarize` returns a placeholder).
- Application-layer encryption at rest (relies on the cloud provider's storage-layer encryption once deployed).
- The spec's aspirational "9 specialized agents" breakdown is implemented as
  5 in practice (base, briefing, calendar, chat, email/task) — the spec
  itself frames this as an idea rather than a hard requirement.
- Real-time collaborative presence (who else is viewing a document/meeting live).

None of the above are defects — they're scoped-out or lower-priority
features. See `BUILD_HISTORY.md` for the full list of bugs that *were*
found and fixed, and exactly how each was verified.
