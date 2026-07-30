import os

from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
backend_url = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery = Celery('eois', broker=broker_url, backend=backend_url)

celery.conf.beat_schedule = {
    'poll-emails': {
        'task': 'poll_emails',
        'schedule': 300.0,
    },
    'sync-calendar': {
        'task': 'sync_calendar',
        'schedule': 600.0,
    },
    'sync-onedrive': {
        'task': 'sync_onedrive',
        'schedule': 1800.0,
    },
    'poll-teams': {
        'task': 'poll_teams',
        'schedule': 300.0,
    },
    'send-meeting-reminders': {
        'task': 'send_meeting_reminders',
        'schedule': 300.0,
    },
    'check-overdue-tasks': {
        'task': 'check_overdue_tasks',
        'schedule': 900.0,
    },
    'generate-daily-briefing': {
        'task': 'generate_daily_briefing',
        'schedule': 86400.0, 
    },
}
celery.conf.timezone = 'Africa/Lagos'

# autodiscover_tasks() expects a Django-style `<package>.tasks` submodule;
# these task modules live flat inside the `tasks` package, so import them
# explicitly to make sure they actually register with this Celery app.
from tasks import (  # noqa: E402,F401
    calendar_sync,
    daily_briefing,
    email_polling,
    notifications,
    onedrive_indexing,
    teams_polling,
)
