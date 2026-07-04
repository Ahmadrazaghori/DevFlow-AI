# DevFlow AI

> **Requirements in. Organized sprints, tracked tasks, and reviewed code out.**
> DevFlow AI is an AI-powered software engineering & DevOps management platform built to replace the scattered toolchain (Jira + Confluence + a code review tool + a bug tracker) with one intelligent system — where an LLM actively analyzes requirements, generates documentation, reviews code, and flags bugs, instead of just storing tickets.

---

##  Build Status: Phase 4 of 11 — Core Domain Complete

This project is being built in public, phase by phase, with each phase fully tested before moving to the next.

| Phase | Module | Status |
|-------|--------|--------|
| 1 | Docker services (Postgres, Redis, backend, Celery workers) | ✅ Done |
| 2 | Database layer & migrations (Alembic) | ✅ Done |
| 3 | Authentication (JWT access/refresh tokens, register/login/logout) | ✅ Done |
| 4 | Core Domain — Organizations, Projects, Sprints, Tasks, RBAC (41 routes) | ✅ Code complete, deployment in progress |
| 5–11 | AI requirement analysis, doc generation, code review, bug detection, notifications, activity logs, full API/deployment docs | 🔜 Planned |

Full architecture, API reference, and deployment guide will be published in **Phase 11**, once every module is built and integration-tested end to end.

---

## What makes this different

Most "project management" clones stop at CRUD for tickets. DevFlow AI is being built with an AI layer baked into the workflow itself:

- **Organizations → Projects → Sprints → Tasks** hierarchy with proper multi-tenant structure
- **Role-based access control (RBAC)** at two levels — organization roles (`OWNER` / `ADMIN` / `MEMBER`) and project roles (`MANAGER` / `DEVELOPER` / `VIEWER`)
- **JWT-based auth** with short-lived access tokens (15 min) and rotating refresh tokens
- **AI-driven modules (upcoming)**: automated requirement analysis, documentation generation, code review, and bug detection powered by the Anthropic API

---

## Tech Stack

- **Backend**: FastAPI (Python), Clean Architecture (`api → application → domain → infrastructure`)
- **Database**: PostgreSQL + SQLAlchemy (async) + Alembic migrations
- **Cache / Queue**: Redis + Celery workers
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Infra**: Docker Compose, Nginx reverse proxy
- **Auth**: JWT (access + refresh tokens), bcrypt password hashing

---

## Running it locally

1. **Copy environment templates**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

2. **Fill in `backend/.env`** — at minimum set `SECRET_KEY`, `POSTGRES_PASSWORD`, `REDIS_PASSWORD`, SMTP credentials, and `ANTHROPIC_API_KEY`.

3. **Start the stack**
   ```bash
   docker compose up --build
   ```

4. **Verify**
   - Backend health check: `http://localhost/health`
   - Swagger docs: `http://localhost/api/docs`
   - Frontend: `http://localhost/`

---

## Project structure

Clean Architecture, organized by layer under `backend/app/`:

```
backend/app/
├── api/v1/            # Route handlers (auth, organizations, projects, sprints, tasks)
├── application/       # Business logic — services & use cases
├── domain/            # Entities & repository interfaces (framework-agnostic)
├── infrastructure/    # Database models, repositories, email, AI integrations
└── core/              # Config, security (JWT), exceptions, logging
```

Frontend follows a feature-sliced structure under `frontend/src/`.

See `docs/ARCHITECTURE.md` (added in Phase 11) for the full breakdown.

---

## Why this project exists

Built as a portfolio-grade demonstration of production DevOps + backend engineering practices: proper environment separation, Dockerized services, layered architecture, RBAC-secured APIs, and a real CI-ready deployment pipeline — not a tutorial clone.

---

## License

MIT — see [LICENSE](./LICENSE).
