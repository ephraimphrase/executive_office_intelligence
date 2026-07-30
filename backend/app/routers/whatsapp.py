from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.whatsapp import WhatsAppMessage
from app.schemas.whatsapp import WhatsAppMessageResponse
from app.services.whatsapp import (
    get_whatsapp_stats,
    process_incoming_message,
    verify_webhook,
)

router = APIRouter()

@router.get("/webhook")
async def webhook_verification(
    request: Request
) -> Any:
    """Webhook verification (GET with hub.challenge)."""
    hub_mode = request.query_params.get("hub.mode")
    hub_challenge = request.query_params.get("hub.challenge")
    hub_verify_token = request.query_params.get("hub.verify_token")
    
    if hub_mode == "subscribe" and hub_verify_token:
        if verify_webhook(hub_verify_token):
            return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def receive_message(
    payload: dict,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Receive incoming WhatsApp messages."""
    await process_incoming_message(payload, db)
    return {"status": "ok"}

@router.get("/messages", response_model=list[WhatsAppMessageResponse])
async def list_messages(
    limit: int = Query(50),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """List processed WhatsApp messages."""
    query = select(WhatsAppMessage).order_by(WhatsAppMessage.received_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/messages/{message_id}", response_model=WhatsAppMessageResponse)
async def get_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get message detail."""
    message = await db.get(WhatsAppMessage, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message

@router.get("/stats")
async def whatsapp_stats(
    db: AsyncSession = Depends(get_db)
) -> Any:
    """WhatsApp integration statistics."""
    stats = await get_whatsapp_stats(db)
    return stats
