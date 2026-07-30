# External Setup Checklist

Everything EOIS needs from outside the codebase to turn its already-built
integrations from mock mode to real. Every item below maps to a specific
`.env` value the code already reads — nothing here requires new code, only
provisioning + configuration.

---

## 1. Azure AD (Entra ID) tenant + App Registration

**Unlocks:** Entra login, Microsoft Teams integration, and the real (non-mock)
Graph email/calendar/OneDrive sync — all three are fully coded, just inert
without credentials.

**If you don't have a tenant yet:** join the [Microsoft 365 Developer Program](https://developer.microsoft.com/en-us/microsoft-365/dev-program)
— free, gives an instant E5 sandbox tenant (25 licenses, 90 days, renews
automatically while you're active in it) pre-loaded with Teams/email/calendar
sample data. Good for building against before pointing this at Dangote's real
tenant.

**Steps:**
1. Sign in to the [Microsoft Entra admin center](https://entra.microsoft.com) → **App registrations** → **New registration**. Name it, choose "Single tenant," **Register**.
2. **Certificates & secrets** → **New client secret** → copy the value immediately (shown once, never again).
3. **API permissions** → **Add a permission** → **Microsoft Graph**:
   - Delegated (for SSO login): `User.Read`, `openid`, `profile`, `email`
   - Application (for background sync): `Mail.Read`, `Calendars.ReadWrite`, `Files.Read.All`, `Chat.Read`, `ChatMessage.Read`, `Team.ReadBasic.All`, `Channel.ReadBasic.All`
   - Click **Grant admin consent for [tenant]** — needs a Global or Application Admin.
4. **Authentication** → **Add a platform** → **Web** → redirect URI `http://localhost:3000/auth/callback` (add your production URL later, same field).
5. Copy: **Application (client) ID**, **Directory (tenant) ID**, and the client secret from step 2.

**Set:**
```
# backend/.env
AZURE_CLIENT_ID=...
AZURE_CLIENT_SECRET=...
AZURE_TENANT_ID=...
AZURE_AUTHORITY=https://login.microsoftonline.com/<tenant-id>

# frontend/.env.local
NEXT_PUBLIC_AZURE_CLIENT_ID=...
NEXT_PUBLIC_AZURE_TENANT_ID=...
```

---

## 2. OpenAI API key (or Azure OpenAI)

**Unlocks:** every AI feature actually being real — email/WhatsApp/Teams
extraction, embeddings for semantic search, chat, briefing generation. Right
now all of it runs against a mock that returns canned or pseudo-random
output. This is the single highest-leverage item on this list.

**Steps:**
1. [platform.openai.com](https://platform.openai.com) → sign in → **Settings → Billing** → add a payment method (required before any key works).
2. [platform.openai.com/api-keys](https://platform.openai.com/api-keys) → **Create new secret key** → copy immediately (shown once).

**Set:**
```
OPENAI_API_KEY=...
```

**Alternative — Azure OpenAI:** base models (GPT-4o family) are generally
ungated now; request access at [aka.ms/oai/access](https://aka.ms/oai/access)
only if you hit a gate. Then Azure Portal → **Create a resource** → **Azure
OpenAI** → deploy a model. Approval, when needed, typically takes 1–5
business days.

---

## 3. Production PostgreSQL with pgvector

**Unlocks:** real semantic document search, and moving off SQLite dev mode.

**Steps:**
1. Azure Portal → **Create a resource** → **Azure Database for PostgreSQL** → **Flexible Server** → configure compute/storage/admin login → **Review + create**.
2. Once it exists: resource → **Settings → Parameters** → find **`azure.extensions`** → add `VECTOR` to the allow-list → **Save**. (The extension's actual name is `vector`, not `pgvector` — that's the community nickname; use `vector` everywhere you allow-list or `CREATE EXTENSION` it.)
3. Verify: connect via `psql` and run `SHOW azure.extensions;` — confirm `vector` is listed. The app itself also tries `CREATE EXTENSION IF NOT EXISTS vector` automatically on startup once the allow-list step above is done.

**Set:**
```
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:5432/<db>
DATABASE_URL_SYNC=postgresql://<user>:<pass>@<host>:5432/<db>
```

---

## 4. Azure Blob Storage

**Unlocks:** uploaded documents actually surviving a backup/restore. Without
this, uploads silently fall back to local disk on the app server — see
`docs/BACKUP_AND_DR.md`.

**Steps:**
1. Azure Portal → **Create a resource** → **Storage account** → configure → **Review + create**.
2. Resource → **Security + networking → Access keys** → **Show** → copy the **Connection string**.
3. **Data storage → Containers** → **+ Container** → create one (e.g. `eois-documents`).

**Set:**
```
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_STORAGE_CONTAINER=eois-documents
```

---

## 5. WhatsApp Business Platform (Meta)

**Unlocks:** the WhatsApp integration going from mock to real — fully coded,
including AI extraction and auto-scheduling.

**Steps:**
1. [developers.facebook.com](https://developers.facebook.com) → **My Apps** → **Create App** → type **Business** → add the **WhatsApp** product.
2. **WhatsApp → API Setup** tab → copy the **Phone number ID** (a numeric ID, not the phone number itself).
3. The temporary token shown there expires in 24h — for a permanent one: **Meta Business Settings → System Users → Add** → create a system user → generate a token with `whatsapp_business_messaging` + `whatsapp_business_management` permissions → copy immediately (shown once).
4. Make up your own **Verify Token** string — it's just a shared secret for the webhook handshake, you choose the value.

**Set:**
```
WHATSAPP_ACCESS_TOKEN=...
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_VERIFY_TOKEN=<any string you choose>
```

---

## 6. Redis (production)

**Unlocks:** Celery background jobs (email/Teams/calendar polling, briefing
generation, notifications) running against something durable instead of
`localhost`.

**Steps:**
1. Azure Portal → **Create a resource** → **Azure Cache for Redis** → **Basics** (name, region, pricing tier) → **Networking** → **Advanced** (choose auth method) → **Review + create**. Takes ~15–20 minutes to deploy.
2. Once running: **Settings → Access keys** → copy the connection details.

**Set:**
```
REDIS_URL=...
CELERY_BROKER_URL=...
CELERY_RESULT_BACKEND=...
```

---

## 7. Deployment basics

- **Domain + TLS** for wherever this actually runs — needed for the Entra
  redirect URI, `ALLOWED_ORIGINS`, and the frontend's `API_BASE_URL` (still
  hardcoded to `localhost:8000` — untouched until a real domain exists).
- **Real `SECRET_KEY`** — generate one, don't reuse the `.env.example`
  placeholder:
  ```
  openssl rand -hex 32
  ```

---

## 8. Two things to confirm, not provision

- **The real GVP user account.** All the auto-create/reschedule automation
  (email/WhatsApp/Teams → tasks/events) resolves its owner via a `User` row
  matching `GVP_EMAIL` in config (currently the placeholder
  `gvp@dangote.com`). That user needs to actually exist in the database, or
  the automation silently no-ops. Either create it yourself once the app is
  running, or tell me the real address and I'll seed it.
- **The actual "Group Vice President – Executive Daily Schedule" Word
  template.** The original spec doc references an uploaded template the
  generator should match exactly. Right now it's a generic Date/Time/Agenda/
  Venue/Notes/Owner table. If you have the real file, send it and I'll match
  the actual layout/branding instead of the generic approximation.

---

## Quick reference — where each `.env` var comes from

| Variable | Source |
|---|---|
| `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, `AZURE_TENANT_ID`, `AZURE_AUTHORITY` | §1 |
| `NEXT_PUBLIC_AZURE_CLIENT_ID`, `NEXT_PUBLIC_AZURE_TENANT_ID` | §1 |
| `OPENAI_API_KEY` | §2 |
| `DATABASE_URL`, `DATABASE_URL_SYNC` | §3 |
| `AZURE_STORAGE_CONNECTION_STRING`, `AZURE_STORAGE_CONTAINER` | §4 |
| `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_VERIFY_TOKEN` | §5 |
| `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | §6 |
| `SECRET_KEY`, `ALLOWED_ORIGINS` | §7 |
| `GVP_EMAIL` | §8 |
