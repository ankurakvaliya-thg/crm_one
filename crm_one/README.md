# Enterprise Python CRM Backend

A modern, production-grade **Customer Relationship Management (CRM) Backend** built using **FastAPI**, **Async SQLAlchemy 2.0**, **Pydantic v2**, **JWT Authentication with Role-Based Access Control (RBAC)**, and **Pytest**.

---

## Key Features

- **Authentication & RBAC**: OAuth2 JWT Bearer Tokens with role-based access levels (`ADMIN`, `SALES_MANAGER`, `SALES_REP`).
- **Account (Company) Management**: Track corporate profiles, industry, revenue, and assigned account managers.
- **Contact Management**: Individual contact records linked to organizations and sales reps.
- **Lead Management & Conversion**: Lead tracking (`NEW`, `CONTACTED`, `QUALIFIED`, `UNQUALIFIED`) with an automated conversion endpoint that transforms qualified leads into an `Account + Contact + Deal`.
- **Sales Deal Pipeline**: Kanban-style sales stage progression (`QUALIFICATION`, `NEEDS_ANALYSIS`, `PROPOSAL`, `NEGOTIATION`, `CLOSED_WON`, `CLOSED_LOST`) with win probability calculation.
- **Tasks & Activities**: Schedule Calls, Meetings, Emails, and Follow-up reminders linked to contacts or deals.
- **Analytics & Dashboard Reports**: Real-time sales metrics including lead conversion rates, total pipeline revenue, deal stage distribution, and open tasks.
- **Automated Testing**: 100% async test suite powered by `pytest`, `pytest-asyncio`, and `httpx`.

---

## Directory Structure

```
.
├── app/
│   ├── main.py                # FastAPI entry point & CORS configuration
│   ├── core/                  # Security, DB session, & app settings
│   ├── models/                # SQLAlchemy 2.0 ORM domain entities
│   ├── schemas/               # Pydantic v2 request/response schemas
│   ├── crud/                  # Async CRUD operations & lead conversion logic
│   └── api/
│       ├── deps.py            # Security & RBAC dependencies
│       └── v1/                # REST API routes (Auth, Users, Accounts, Leads, Deals, Tasks, Analytics)
├── scripts/                   # DB setup helpers
├── tests/                     # Automated async integration tests
├── alembic/                   # Database migration scripts
├── Dockerfile                 # Container build definition
├── docker-compose.yml         # Container orchestration with PostgreSQL
├── requirements.txt           # Project dependencies
└── README.md
```

---

## Quick Start

### 1. Prerequisites
- Python 3.10+
- Virtual Environment tool (`venv`)

### 2. Setup Virtual Environment & Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### 4. Run Development Server

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

---

## API Documentation

FastAPI automatically generates interactive Swagger & ReDoc API documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Key Endpoint Highlights

| Method | Endpoint | Description | Permission |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auth/register` | Register a new user | Public |
| `POST` | `/api/v1/auth/login` | OAuth2 Password Login (returns JWT) | Public |
| `GET` | `/api/v1/auth/me` | Get active user profile | Authenticated |
| `GET` | `/api/v1/leads` | List sales leads | Authenticated |
| `POST` | `/api/v1/leads` | Create new lead | Authenticated |
| `POST` | `/api/v1/leads/{id}/convert` | **Convert Lead -> Account + Contact + Deal** | Authenticated |
| `GET` | `/api/v1/deals` | List deals in sales pipeline | Authenticated |
| `PUT` | `/api/v1/deals/{id}` | Update deal stage & probability | Authenticated |
| `GET` | `/api/v1/analytics/dashboard` | Get CRM analytics & sales stats | Authenticated |

---

## Running Automated Tests

Run the test suite using `pytest`:

```bash
pytest -v
```

---

## Docker Deployment (Production Ready)

To launch the full backend alongside a PostgreSQL database using Docker Compose:

```bash
docker-compose up -d --build
```
