"""Compatibility shim — re-exports MeetingRecord as Meeting for router."""
from app.models.meeting_record import MeetingRecord

# Alias
Meeting = MeetingRecord
