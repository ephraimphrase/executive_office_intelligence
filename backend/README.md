# EOIS Backend — Executive Office Intelligence System

## Overview
The backend for the Executive Office Intelligence System (EOIS), serving as the AI-powered
Chief of Staff for the Group Vice President of Dangote Group.

## Architecture
This is a modern async Python backend utilizing FastAPI for high-performance REST APIs, 
PostgreSQL for relational data persistence, Redis for caching and message brokering, 
Celery for distributed background tasks, and OpenAI for core intelligence and AI features.

## Quick Start
### Prerequisites
- Docker & Docker Compose
- Python 3.11+

### Development Setup
1. Clone the repository
2. Copy .env.example to .env and fill in values
3. Run `docker-compose up -d db redis`
4. Install Python deps: `pip install -r requirements.txt`
5. Run migrations: `alembic upgrade head`
6. Start API: `uvicorn app.main:app --reload`
7. Start worker: `celery -A celery_app worker --loglevel=info`

### Docker Setup (Full Stack)
```bash
docker-compose up -d
```

## API Documentation
Once running: http://localhost:8000/docs

## Integration Status
Table showing which integrations need credentials:
| Integration | Status | Required Env Vars |
|-------------|--------|------------------|
| Microsoft Graph (Email/Calendar/OneDrive) | Needs credentials | AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID |
| OpenAI (AI Brain) | Needs credentials | OPENAI_API_KEY |
| WhatsApp Business | Needs credentials | WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_ACCESS_TOKEN |
| Azure AI Search | Needs credentials | AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY |
| Azure Blob Storage | Needs credentials | AZURE_STORAGE_CONNECTION_STRING |

All integrations fall back to mock data in development mode when credentials are not provided.

## Environment Variables
Copy `.env.example` to `.env` and provide your specific keys.

## Project Structure
- `app/`: FastAPI application code
- `alembic/`: Database migrations
- `agents/`: AI agents and flows
- `tasks/`: Celery background tasks
