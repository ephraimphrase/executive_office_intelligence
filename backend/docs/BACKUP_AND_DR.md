# Backup & Disaster Recovery Runbook

This is deployment configuration, not application code — EOIS doesn't need a
custom backup job as long as it's deployed on managed services with their
backup features turned on. This doc says exactly what to turn on and how to
restore.

## What actually needs backing up

| Data | Where it lives | Criticality |
|---|---|---|
| Everything (users, tasks, decisions, commitments, risks, emails, meetings, briefings, audit logs, etc.) | PostgreSQL | **Critical** — this is the system of record |
| Uploaded documents (Word/PDF/Excel/PPT) | Azure Blob Storage (falls back to local disk only if `AZURE_STORAGE_CONNECTION_STRING` is unset — see warning below) | **Critical** |
| Redis (Celery broker/result backend) | Redis | Not critical — purely ephemeral queue/cache state, safe to lose and let Celery re-populate |
| `.env` secrets (`SECRET_KEY`, API keys, connection strings) | Wherever you manage secrets | Critical to *retain*, not to version-back-up in the DB sense — losing these means re-provisioning credentials, not data loss |

**Warning:** if `AZURE_STORAGE_CONNECTION_STRING` is not configured, uploaded
documents are written to local disk on the app server (`uploads/`) and are
**not covered by any of the steps below**. Configure blob storage before
relying on this runbook for document durability.

## 1. PostgreSQL — Azure Database for PostgreSQL Flexible Server

1. **Automated backups** are on by default and cannot be disabled — Azure takes
   daily snapshots + continuous transaction log archiving automatically.
2. Set retention: Portal → your server → *Backup and restore* → **Backup retention period**.
   Recommend **35 days** (the max) for an executive system; compliance may
   dictate longer via a separate long-term retention policy if needed.
3. Enable **geo-redundant backup storage** at server creation time (this
   *cannot* be changed after the server is created — if the server already
   exists as locally-redundant, you'd need to provision a new server and
   migrate to change this).
4. Point-in-time restore (PITR): Portal → server → *Restore* → pick a
   timestamp within the retention window → restores to a **new** server
   (Azure never overwrites the original). Update `DATABASE_URL` /
   `DATABASE_URL_SYNC` to point at the restored server once verified.

### If instead using AWS RDS for PostgreSQL
- Enable **Automated backups** (Modify → Backup retention period, 1–35 days).
- Enable **Multi-AZ** for failover, not a backup substitute — still keep automated backups on.
- Restore via *Actions → Restore to point in time*, which similarly creates a new instance.

## 2. Document storage — Azure Blob Storage

1. Configure `AZURE_STORAGE_CONNECTION_STRING` and `AZURE_STORAGE_CONTAINER`
   in `.env` — once set, `app/integrations/azure_blob.py` automatically
   switches from local-disk fallback to real blob storage for all uploads
   (see `app/routers/documents.py`).
2. On the Storage Account: enable **soft delete for blobs** (Data protection
   blade) — recommend a 30-day retention window, so accidental deletes are
   recoverable without a full restore.
3. Enable **blob versioning** on the same blade — keeps prior versions when a
   blob is overwritten.
4. Set the storage account's replication to **GRS** (geo-redundant) or
   **RA-GRS** if you want read access to the secondary region — this is a
   setting at account creation (can be upgraded later without downtime, LRS
   → GRS is a supported migration).

## 3. Restore drill (do this at least once, not just in theory)

1. Trigger a PITR restore of the database to a *test* server.
2. Point a scratch copy of the backend (`DATABASE_URL` env var only — nothing
   else changes) at the restored server.
3. Confirm `GET /health` reports healthy and spot-check a few records (a
   recent audit log entry, a task, a document row) exist and match what you
   expect from before the restore point.
4. If documents are in blob storage, confirm a `Document.blob_url` from the
   restored DB actually resolves via `AzureBlobClient.download_file` —
   database and blob storage back up on independent schedules, so a DB
   restore can reference a document blob that's since changed or been
   soft-deleted. Reconcile if so.
5. Tear down the scratch restore once verified — don't leave orphaned
   restored servers running (cost, and a second copy of the whole database).

## What this project does *not* need

- **No custom `pg_dump` cron job** — only relevant if self-hosting Postgres
  (e.g., the `docker-compose.yml` `db` service) rather than using a managed
  service. Since the current deployment target is a managed cloud DB, the
  provider's automated backups above are sufficient and simpler than
  maintaining a bespoke dump/restore script.
- **No Redis backup** — it's a queue/cache, not a data store; losing it just
  means in-flight Celery task state resets, not permanent data loss.
