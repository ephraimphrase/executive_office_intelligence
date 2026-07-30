"""Compatibility shim — re-exports EmailRecord as Email for router."""
from app.models.email_record import EmailRecord

# Alias
Email = EmailRecord
