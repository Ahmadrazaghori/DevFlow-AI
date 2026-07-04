# DevFlow AI — Database Schema

Multi-tenant schema: `organizations` is the top-level tenant boundary.
Every `project` belongs to one organization; every task, sprint,
label, AI analysis, and document belongs to one project.

## Entity-Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ ORGANIZATION_MEMBERS : "belongs to"
    USERS ||--o{ PROJECT_MEMBERS : "belongs to"
    USERS ||--o{ ORGANIZATIONS : "owns"
    USERS ||--o{ TASKS : "assigned to"
    USERS ||--o{ TASKS : "reports"
    USERS ||--o{ TASK_COMMENTS : "writes"
    USERS ||--o{ NOTIFICATIONS : "receives"
    USERS ||--o{ REFRESH_TOKENS : "holds"
    USERS ||--o{ AI_ANALYSES : "requests"

    ORGANIZATIONS ||--o{ ORGANIZATION_MEMBERS : "has"
    ORGANIZATIONS ||--o{ PROJECTS : "contains"
    ORGANIZATIONS ||--o{ ACTIVITY_LOGS : "logs"

    PROJECTS ||--o{ PROJECT_MEMBERS : "has"
    PROJECTS ||--o{ SPRINTS : "contains"
    PROJECTS ||--o{ TASKS : "contains"
    PROJECTS ||--o{ LABELS : "defines"
    PROJECTS ||--o{ AI_ANALYSES : "has"
    PROJECTS ||--o{ DOCUMENTS : "has"

    SPRINTS ||--o{ TASKS : "contains"

    TASKS ||--o{ TASK_COMMENTS : "has"
    TASKS ||--o{ AI_ANALYSES : "triggers"
    TASKS }o--o{ LABELS : "tagged with"

    AI_ANALYSES ||--o{ DOCUMENTS : "generates"

    USERS {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        bool is_active
        bool is_verified
        bool is_superuser
    }

    ORGANIZATIONS {
        uuid id PK
        string name
        string slug UK
        uuid owner_id FK
    }

    ORGANIZATION_MEMBERS {
        uuid id PK
        uuid organization_id FK
        uuid user_id FK
        enum role "owner|admin|member"
    }

    PROJECTS {
        uuid id PK
        uuid organization_id FK
        string name
        string key "short code e.g. DEV"
        enum status "active|archived|on_hold"
    }

    PROJECT_MEMBERS {
        uuid id PK
        uuid project_id FK
        uuid user_id FK
        enum role "manager|developer|viewer"
    }

    SPRINTS {
        uuid id PK
        uuid project_id FK
        string name
        enum status "planned|active|completed"
        date start_date
        date end_date
    }

    TASKS {
        uuid id PK
        uuid project_id FK
        uuid sprint_id FK "nullable = backlog"
        uuid assignee_id FK "nullable"
        uuid reporter_id FK
        string title
        enum task_type "feature|bug|chore|improvement"
        enum status "backlog|todo|in_progress|in_review|done"
        enum priority "low|medium|high|urgent"
        int story_points
    }

    LABELS {
        uuid id PK
        uuid project_id FK
        string name
        string color
    }

    TASK_COMMENTS {
        uuid id PK
        uuid task_id FK
        uuid author_id FK
        text content
    }

    AI_ANALYSES {
        uuid id PK
        uuid project_id FK
        uuid task_id FK "nullable"
        uuid requested_by_id FK
        enum analysis_type "requirement_analysis|doc_generation|bug_detection|code_review|sprint_planning|api_generation"
        enum status "pending|processing|completed|failed"
        jsonb input_data
        jsonb output_data
        string celery_task_id
    }

    DOCUMENTS {
        uuid id PK
        uuid project_id FK
        uuid ai_analysis_id FK "nullable"
        string title
        text content
        enum doc_type "readme|api_documentation|architecture|deployment_guide|developer_guide"
        int version
    }

    NOTIFICATIONS {
        uuid id PK
        uuid user_id FK
        enum notification_type
        string title
        bool is_read
    }

    ACTIVITY_LOGS {
        uuid id PK
        uuid organization_id FK
        uuid project_id "nullable, no FK constraint"
        uuid user_id FK "nullable"
        string action
        string entity_type
        jsonb extra_data
    }

    REFRESH_TOKENS {
        uuid id PK
        uuid user_id FK
        string token_hash UK
        datetime expires_at
        bool revoked
    }
```

## Design decisions

- **UUID primary keys** everywhere — avoids sequential-ID enumeration
  attacks and merges cleanly across environments (dev/staging/prod
  seed data won't collide).
- **Multi-tenancy via `organizations`** — every project is scoped to
  an organization; a user's role differs per-organization
  (`organization_members`) and per-project (`project_members`), since
  someone might be an Admin at the org level but only a Developer on
  a specific project.
- **Soft coupling for `activity_logs.project_id`** — intentionally not
  a foreign key, since activity logs should survive project deletion
  for audit purposes (append-only compliance record).
- **`refresh_tokens` stores only a hash**, never the raw token — a
  database leak alone can't be used to forge a session.
- **JSONB for AI analysis input/output** — each of the 6 AI analysis
  types has a different result shape (a code review result looks
  nothing like a sprint plan), so a flexible JSONB column avoids
  either a sparse table or six near-duplicate tables.
