from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.report import export_report_to_file as export_report
from app.services.report import generate_action_register_report
from app.services.report import generate_decision_register_report
from app.services.report import generate_word_schedule_report as generate_word_schedule
from app.services.report import (
    get_commitment_tracking_report as generate_commitment_report,
)
from app.services.report import get_email_analytics as generate_email_analytics
from app.services.report import get_executive_summary as generate_exec_summary
from app.services.report import get_meeting_statistics as generate_meeting_stats
from app.services.report import get_task_completion_report as generate_task_report

router = APIRouter()

@router.get("/executive-summary")
async def executive_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Comprehensive executive summary for a date range."""
    report = await generate_exec_summary(start_date, end_date, db)
    return report

@router.get("/task-completion")
async def task_completion(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Task completion report by department."""
    report = await generate_task_report(db)
    return report

@router.get("/meeting-statistics")
async def meeting_statistics(
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Meeting stats (count, avg duration, attendance)."""
    stats = await generate_meeting_stats(start_date, end_date, db)
    return stats

@router.get("/commitment-tracking")
async def commitment_tracking(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Commitment fulfillment report."""
    report = await generate_commitment_report(db)
    return report

@router.get("/email-analytics")
async def email_analytics(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Email volume, response time analytics."""
    analytics = await generate_email_analytics(start_date, end_date, db)
    return analytics

@router.post("/word-schedule")
async def word_schedule(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Generate Word schedule for date range, returns file."""
    file_content = await generate_word_schedule(start_date, end_date, db)
    return Response(
        content=file_content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="Schedule_{start_date}_to_{end_date}.docx"'},
    )

@router.post("/action-register")
async def action_register(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Generate Word action register of open tasks, returns file."""
    file_content = await generate_action_register_report(db)
    return Response(
        content=file_content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="Action_Register.docx"'},
    )

@router.post("/decision-register")
async def decision_register(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Generate Word executive decision register, returns file."""
    file_content = await generate_decision_register_report(db)
    return Response(
        content=file_content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": 'attachment; filename="Decision_Register.docx"'},
    )

@router.post("/export")
async def export_any_report(
    report_type: str = Query(..., pattern="^(executive|task|meeting|commitment|email)$"),
    format: str = Query("pdf", pattern="^(pdf|excel)$"),
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Export any report to PDF/Excel."""
    today = date.today()
    range_start = start_date or today.replace(day=1)
    range_end = end_date or today

    if report_type == "executive":
        report_data = await generate_exec_summary(range_start, range_end, db)
    elif report_type == "task":
        report_data = await generate_task_report(db)
    elif report_type == "meeting":
        report_data = await generate_meeting_stats(range_start, range_end, db)
    elif report_type == "commitment":
        report_data = await generate_commitment_report(db)
    else:
        report_data = await generate_email_analytics(range_start, range_end, db)

    file_content = await export_report(report_data, format)
    if format == "excel":
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ext = "xlsx"
    else:
        media_type = "application/pdf"
        ext = "pdf"

    return Response(
        content=file_content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{report_type}_report.{ext}"'},
    )
