import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Column, Date, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class Briefing(Base):
    __tablename__ = "briefings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date = Column(Date, unique=True, index=True, nullable=False)
    
    events_summary = Column(JSON, default=dict)
    tasks_summary = Column(JSON, default=dict)
    email_highlights = Column(JSON, default=dict)
    pending_decisions = Column(JSON, default=dict)
    travel_info = Column(JSON, default=dict)
    weather_info = Column(JSON, default=dict)
    risks_summary = Column(JSON, default=dict)
    talking_points = Column(JSON, default=list)
    suggested_priorities = Column(JSON, default=list)
    critical_alerts = Column(JSON, default=list)
    
    full_content = Column(JSON, default=dict) # Complete briefing structure
    
    word_file_url = Column(String, nullable=True)
    pdf_file_url = Column(String, nullable=True)
    
    generated_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    sent_to = Column(JSON, default=list)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
