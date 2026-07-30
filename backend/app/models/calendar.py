"""Compatibility shim — re-exports Event model as expected by calendar router."""
from app.models.event import Event

# Alias
CalendarEvent = Event
