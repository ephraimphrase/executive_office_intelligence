"""Compatibility shim — re-exports event schemas under calendar names."""
from app.schemas.event import EventCreate, EventResponse, EventUpdate

# Aliases for router
CalendarEventCreate  = EventCreate
CalendarEventUpdate  = EventUpdate
CalendarEventResponse = EventResponse
