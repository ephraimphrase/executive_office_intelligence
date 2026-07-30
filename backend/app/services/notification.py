"""Compatibility shim — SSE stream backed directly by the Notification table
(the rest of the notifications router already queries this table directly)."""
import asyncio
import json
from collections.abc import AsyncGenerator


async def get_notification_stream(user_id: str) -> AsyncGenerator[str, None]:
    """Server-Sent Events generator for real-time, unread notifications."""
    from sqlalchemy import select

    from app.database import AsyncSessionLocal
    from app.models.notification import Notification

    seen_ids: set[str] = set()
    while True:
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Notification)
                .where(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
                .order_by(Notification.created_at.desc())
            )
            for notif in result.scalars().all():
                notif_id = str(notif.id)
                if notif_id in seen_ids:
                    continue
                seen_ids.add(notif_id)
                data = {
                    'id': notif_id,
                    'type': notif.type.value if hasattr(notif.type, 'value') else str(notif.type),
                    'title': notif.title,
                    'message': notif.message,
                    'priority': notif.priority.value if hasattr(notif.priority, 'value') else str(notif.priority),
                }
                yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(10)  # poll every 10 seconds
