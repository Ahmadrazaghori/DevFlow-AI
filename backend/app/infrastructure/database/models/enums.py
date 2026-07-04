"""Domain enums shared across models, schemas, and business logic.

Defined once here so the same values are used in the database (as
native PostgreSQL ENUM types), Pydantic schemas, and application code
— no risk of drift between layers.
"""

import enum


class OrganizationRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class ProjectRole(str, enum.Enum):
    MANAGER = "manager"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    ON_HOLD = "on_hold"


class SprintStatus(str, enum.Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"


class TaskStatus(str, enum.Enum):
    BACKLOG = "backlog"
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskType(str, enum.Enum):
    FEATURE = "feature"
    BUG = "bug"
    CHORE = "chore"
    IMPROVEMENT = "improvement"


class AIAnalysisType(str, enum.Enum):
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    DOCUMENTATION_GENERATION = "documentation_generation"
    BUG_DETECTION = "bug_detection"
    CODE_REVIEW = "code_review"
    SPRINT_PLANNING = "sprint_planning"
    API_GENERATION = "api_generation"


class AIAnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentType(str, enum.Enum):
    README = "readme"
    API_DOCUMENTATION = "api_documentation"
    ARCHITECTURE = "architecture"
    DEPLOYMENT_GUIDE = "deployment_guide"
    DEVELOPER_GUIDE = "developer_guide"


class NotificationType(str, enum.Enum):
    TASK_ASSIGNED = "task_assigned"
    TASK_STATUS_CHANGED = "task_status_changed"
    COMMENT_ADDED = "comment_added"
    SPRINT_STARTED = "sprint_started"
    SPRINT_COMPLETED = "sprint_completed"
    AI_ANALYSIS_COMPLETED = "ai_analysis_completed"
    MENTIONED = "mentioned"
    PROJECT_INVITATION = "project_invitation"
