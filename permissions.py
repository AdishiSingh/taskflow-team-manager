"""
Centralized role-based access control for Team Task Manager.
"""

from functools import wraps
from flask import abort
from flask_login import current_user


def admin_required(f):
    """Require authenticated user with admin role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def member_project_access_required(f):
    """
    Require project access: admins see all projects;
    members only projects they belong to.
    Expects project_id as the first route argument.
    """
    @wraps(f)
    def decorated_function(project_id, *args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)

        from models import Project
        project = Project.query.get_or_404(project_id)

        if not current_user.can_access_project(project):
            abort(403)

        return f(project_id, *args, **kwargs)
    return decorated_function
