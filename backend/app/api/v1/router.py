"""Aggregates all API v1 routers."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.auth import router as auth_router
from app.api.v1.organizations import router as organizations_router
from app.api.v1.projects import org_projects_router, projects_router
from app.api.v1.sprints import project_sprints_router, sprints_router
from app.api.v1.tasks import project_labels_router, project_tasks_router, tasks_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(organizations_router)
api_router.include_router(org_projects_router)
api_router.include_router(projects_router)
api_router.include_router(project_sprints_router)
api_router.include_router(sprints_router)
api_router.include_router(project_tasks_router)
api_router.include_router(tasks_router)
api_router.include_router(project_labels_router)
