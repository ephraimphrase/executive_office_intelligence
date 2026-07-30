"""Compatibility shim — re-exports meeting_record schemas under meeting names."""
from app.schemas.meeting_record import (
    MeetingRecordCreate,
    MeetingRecordResponse,
    MeetingRecordUpdate,
)

# Aliases
MeetingCreate   = MeetingRecordCreate
MeetingUpdate   = MeetingRecordUpdate
MeetingResponse = MeetingRecordResponse
