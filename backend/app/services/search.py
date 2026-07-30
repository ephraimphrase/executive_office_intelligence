"""Global search service across all EOIS entities."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def global_search(query: str, entity_type: str = 'all', limit: int = 20, db: AsyncSession = None) -> list:
    """Search across emails, tasks, events, decisions, commitments, risks.
    This does a plain substring (ILIKE) match, so it works best with a
    keyword, not a full natural-language question — see
    agents/orchestrator.py's _extract_search_keywords for the caller that
    turns a chat question into keywords before calling this."""
    results = []
    per_type_limit = limit // 6 + 1

    if entity_type in ('all', 'emails'):
        from app.models.email_record import EmailRecord
        stmt = select(EmailRecord).where(
            EmailRecord.subject.ilike(f'%{query}%') |
            EmailRecord.ai_summary.ilike(f'%{query}%')
        ).limit(per_type_limit)
        res = await db.execute(stmt)
        for r in res.scalars().all():
            results.append({'type': 'email', 'id': str(r.id), 'title': r.subject, 'snippet': r.ai_summary or r.body_preview or ''})

    if entity_type in ('all', 'tasks'):
        from app.models.task import Task
        stmt = select(Task).where(Task.title.ilike(f'%{query}%')).limit(per_type_limit)
        res = await db.execute(stmt)
        for r in res.scalars().all():
            results.append({'type': 'task', 'id': str(r.id), 'title': r.title, 'snippet': r.description or ''})

    if entity_type in ('all', 'decisions'):
        from app.models.decision import Decision
        stmt = select(Decision).where(Decision.description.ilike(f'%{query}%')).limit(per_type_limit)
        res = await db.execute(stmt)
        for r in res.scalars().all():
            results.append({'type': 'decision', 'id': str(r.id), 'title': r.description[:80], 'snippet': r.context or ''})

    if entity_type in ('all', 'events'):
        from app.models.event import Event
        stmt = select(Event).where(Event.title.ilike(f'%{query}%')).limit(per_type_limit)
        res = await db.execute(stmt)
        for r in res.scalars().all():
            results.append({'type': 'event', 'id': str(r.id), 'title': r.title, 'snippet': str(r.start_datetime) if r.start_datetime else ''})

    if entity_type in ('all', 'risks'):
        from app.models.risk import Risk
        stmt = select(Risk).where(Risk.description.ilike(f'%{query}%')).limit(per_type_limit)
        res = await db.execute(stmt)
        for r in res.scalars().all():
            results.append({'type': 'risk', 'id': str(r.id), 'title': r.description[:80], 'snippet': r.category or ''})

    if entity_type in ('all', 'commitments'):
        from app.models.commitment import Commitment
        stmt = select(Commitment).where(Commitment.description.ilike(f'%{query}%')).limit(per_type_limit)
        res = await db.execute(stmt)
        for r in res.scalars().all():
            results.append({'type': 'commitment', 'id': str(r.id), 'title': r.description[:80], 'snippet': r.context or ''})

    if entity_type in ('all', 'documents'):
        from app.models.document import Document
        stmt = select(Document).where(
            Document.name.ilike(f'%{query}%') | Document.ai_summary.ilike(f'%{query}%')
        ).limit(per_type_limit)
        res = await db.execute(stmt)
        for r in res.scalars().all():
            results.append({'type': 'document', 'id': str(r.id), 'title': r.name, 'snippet': r.ai_summary or ''})

    return results[:limit]

async def semantic_search(query: str, top_k: int = 10, db: AsyncSession = None) -> list:
    """Vector/semantic search over indexed documents (pgvector)."""
    from app.services.knowledge_base import KnowledgeBaseService
    kb = KnowledgeBaseService()
    docs = await kb.search(query, top_k, {}, db)
    return [
        {'type': 'document', 'id': str(doc.id), 'title': doc.name, 'snippet': doc.ai_summary or ''}
        for doc in docs
    ]

async def get_search_suggestions(query: str, db: AsyncSession = None) -> list:
    """Return autocomplete suggestions."""
    suggestions = [
        "What is happening today?",
        "Show overdue tasks",
        "Pending board papers",
        "Unresolved commitments",
        "Critical emails",
        "Upcoming travel",
        "Recent decisions",
    ]
    if query:
        return [s for s in suggestions if query.lower() in s.lower()][:5]
    return suggestions[:5]
