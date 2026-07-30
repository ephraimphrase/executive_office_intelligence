import io
import re
from datetime import datetime, timezone


def paginate(query, skip: int, limit: int):
    """Pagination helper"""
    return query.offset(skip).limit(limit)

def format_datetime(dt: datetime) -> str:
    """Consistent datetime formatting"""
    if not dt:
        return ""
    return dt.isoformat()

def generate_token(length: int = 32) -> str:
    """Random token generation"""
    import secrets
    return secrets.token_hex(length // 2)

def sanitize_filename(name: str) -> str:
    """Safe filenames"""
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', name)

async def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from docx using python-docx"""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        import logging
        logging.error(f"Failed to extract docx: {e}")
        return ""

async def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from pdf using pdfplumber"""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return "\n".join([page.extract_text() or '' for page in pdf.pages])
    except Exception as e:
        import logging
        logging.error(f"Failed to extract pdf: {e}")
        return ""

def calculate_priority_score(priority: int, due_date: datetime, created_at: datetime) -> float:
    """Calculate priority score for sorting"""
    score = float(priority) * 10
    now = datetime.now(timezone.utc)
    if due_date:
        days_until_due = (due_date - now).days
        if days_until_due < 0:
            score += 50  # Overdue
        elif days_until_due < 3:
            score += 20  # Due soon
    
    # Slight bump for newer items
    age_days = (now - created_at).days
    score += max(0, 10 - age_days)
    
    return score
