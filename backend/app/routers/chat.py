from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.chat import ChatMessage
from app.schemas.chat import ChatRequest as ChatMessageCreate
from app.schemas.chat import ChatResponse as ChatMessageResponse
from app.services.chat import (
    clear_chat_history,
    generate_chat_suggestions,
    get_chat_history,
    process_chat_message,
)

router = APIRouter()

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    message_in: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Send message to AI assistant, returns response."""
    response = await process_chat_message(str(current_user.id), message_in.message, message_in.conversation_id, db)
    return response

@router.get("/history", response_model=list[ChatMessage])
async def get_history(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get conversation history."""
    history = await get_chat_history(str(current_user.id), limit)
    return history

@router.delete("/history")
async def clear_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Clear conversation history."""
    await clear_chat_history(str(current_user.id))
    return {"message": "Chat history cleared"}

@router.get("/suggestions", response_model=list[str])
async def get_suggestions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get suggested queries based on current context."""
    suggestions = await generate_chat_suggestions(current_user.id, db)
    return suggestions
