"""
REST API routes for Team Task Manager.

All endpoints return JSON and require an authenticated session (login_required).
Use the same browser session cookie after logging in via /auth/login.

Example responses:

GET /api/projects
{
  "success": true,
  "count": 2,
  "projects": [
    {
      "id": 1,
      "name": "AI Resume Analyzer",
      "description": "...",
      "created_by": 2,
      "members_count": 3
    }
  ]
}

GET /api/project/1
{
  "success": true,
  "project": {
    "id": 1,
    "name": "...",
    "description": "...",
    "created_by": 2,
    "members_count": 3,
    "members": [{"id": 2, "name": "...", "email": "...", "role": "admin"}],
    "tasks": [{"id": 1, "title": "...", "status": "Pending", ...}]
  }
}
"""

from flask import Blueprint, jsonify, abort
from flask_login import login_required, current_user
from models import Project, Task

api_bp = Blueprint('api', __name__)


# ---------------------------------------------------------------------------
# JSON serialization helpers
# ---------------------------------------------------------------------------

def _format_date(value):
    """Serialize date/datetime values for JSON."""
    if value is None:
        return None
    return value.isoformat()


def serialize_member(user):
    """Serialize a project member for API responses."""
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
    }


def serialize_task(task, include_project_name=True):
    """Serialize a task for API responses."""
    data = {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'due_date': _format_date(task.due_date),
        'assigned_to': task.assigned_to,
        'project_id': task.project_id,
    }
    if include_project_name:
        data['project_name'] = task.project.name if task.project else None
    return data


def serialize_project_summary(project):
    """Serialize a project list item (summary fields only)."""
    return {
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'created_by': project.created_by,
        'members_count': len(project.members),
    }


def serialize_project_detail(project):
    """Serialize full project details including members and tasks."""
    return {
        **serialize_project_summary(project),
        'created_at': _format_date(project.created_at),
        'creator_name': project.creator.name if project.creator else None,
        'members': [serialize_member(m) for m in project.members],
        'tasks': [serialize_task(t) for t in project.tasks],
    }


def api_error(message, status_code):
    """Return a consistent JSON error response."""
    response = jsonify({
        'success': False,
        'error': message,
    })
    response.status_code = status_code
    return response


def get_accessible_tasks():
    """Tasks visible to the current user (role-aware)."""
    if current_user.is_admin():
        return Task.query.order_by(Task.created_at.desc()).all()
    project_ids = current_user.get_member_project_ids()
    if not project_ids:
        return []
    return Task.query.filter(Task.project_id.in_(project_ids)).order_by(
        Task.created_at.desc()
    ).all()


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@api_bp.route('/projects', methods=['GET'])
@login_required
def list_projects():
    """
    GET /api/projects
    Return all projects the current user can access.
    Admins receive every project; members receive assigned projects only.
    """
    projects = current_user.get_accessible_projects()
    return jsonify({
        'success': True,
        'count': len(projects),
        'projects': [serialize_project_summary(p) for p in projects],
    })


@api_bp.route('/project/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    """
    GET /api/project/<id>
    Return a single project with its members and tasks.
    Returns 404 if not found, 403 if the user lacks access.
    """
    project = Project.query.get(project_id)
    if not project:
        return api_error('Project not found', 404)

    if not current_user.can_access_project(project):
        return api_error('Access denied to this project', 403)

    return jsonify({
        'success': True,
        'project': serialize_project_detail(project),
    })


@api_bp.route('/tasks', methods=['GET'])
@login_required
def list_tasks():
    """
    GET /api/tasks
    Return all tasks the current user can access.
    Admins receive every task; members receive tasks from their projects.
    """
    tasks = get_accessible_tasks()
    return jsonify({
        'success': True,
        'count': len(tasks),
        'tasks': [serialize_task(t) for t in tasks],
    })


@api_bp.route('/task/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    """
    GET /api/task/<id>
    Return a single task with full details.
    Returns 404 if not found, 403 if the user lacks access.
    """
    task = Task.query.get(task_id)
    if not task:
        return api_error('Task not found', 404)

    if not current_user.is_admin() and not current_user.can_access_project(task.project):
        return api_error('Access denied to this task', 403)

    return jsonify({
        'success': True,
        'task': serialize_task(task),
    })
