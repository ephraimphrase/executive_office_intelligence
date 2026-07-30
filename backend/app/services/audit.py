import logging

logger = logging.getLogger(__name__)


async def log_action(db, actor, action: str, resource_type: str | None = None,
                      resource_id=None, details: dict | None = None, ip_address: str | None = None) -> None:
    """Best-effort audit trail write. Never raises and never blocks the caller's
    primary operation — a failed audit write should not fail the request it's
    describing, only be logged for someone to notice."""
    if db is None:
        return
    try:
        from app.models.audit_log import AuditLog

        entry = AuditLog(
            actor_user_id=getattr(actor, "id", None),
            actor_email=getattr(actor, "email", None),
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id is not None else None,
            details=details or {},
            ip_address=ip_address,
        )
        db.add(entry)
        await db.commit()
    except Exception as e:
        logger.warning(f"Audit log write failed for action={action}: {e}")
