"""Compatibility shim — re-exports email_record schemas under email names."""
from app.schemas.email_record import (
    EmailRecordCreate,
    EmailRecordResponse,
    EmailRecordUpdate,
)

# Aliases
EmailCreate   = EmailRecordCreate
EmailUpdate   = EmailRecordUpdate
EmailResponse = EmailRecordResponse
EmailStatusUpdate = EmailRecordUpdate  # reuse update schema
