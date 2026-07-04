# DevFlow AI

> **Status: Step 1 — Project Scaffolding.** This is not the final README.
> Full documentation (architecture, API reference, deployment guide,
> developer guide) is produced in Phase 11 once all modules are built.

AI-Powered Software Engineering & DevOps Management Platform.

## Running the Step 1 scaffold locally

1. Copy environment templates:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```
2. Fill in `backend/.env`: at minimum set `SECRET_KEY`, `POSTGRES_PASSWORD`,
   `REDIS_PASSWORD`, SMTP credentials, and `ANTHROPIC_API_KEY`.
3. Start the stack:
   ```bash
   docker compose up --build
   ```
4. Verify:
   - Backend health check: `http://localhost/health`
   - Swagger docs: `http://localhost/api/docs`
   - Frontend: `http://localhost/`

At this stage the backend only exposes `/health` — no business endpoints
exist yet. Those arrive in Phase 3 onward.

## Project structure

See `docs/ARCHITECTURE.md` (added in Phase 11) for the full breakdown.
For now, refer to the folder layout under `backend/app/` (Clean
Architecture: `api` → `application` → `domain` ← `infrastructure`) and
`frontend/src/` (feature-sliced).
