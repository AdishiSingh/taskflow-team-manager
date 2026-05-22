"""
Dashboard routes for Team Task Manager.
Provides statistics and overview of tasks and projects.
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)


def _format_activity_time(dt):
    """Human-readable relative time for activity feed."""
    if not dt:
        return 'Recently'
    delta = datetime.utcnow() - dt
    minutes = int(delta.total_seconds() / 60)
    if minutes < 1:
        return 'Just now'
    if minutes < 60:
        return f'{minutes}m ago'
    hours = minutes // 60
    if hours < 24:
        return f'{hours}h ago'
    days = hours // 24
    return f'{days}d ago'


def build_activity_feed(tasks, limit=8):
    """Build activity timeline from existing task data (no new DB table)."""
    activities = []

    for task in sorted(tasks, key=lambda t: t.created_at, reverse=True)[:25]:
        project_name = task.project.name if task.project else 'Project'
        assignee = task.assigned_user.name if task.assigned_user else None

        if task.status == 'Completed':
            actor = assignee or 'A team member'
            activities.append({
                'icon': 'bi-check-circle-fill',
                'color': 'success',
                'message': f'{actor} completed <strong>{task.title}</strong>',
                'detail': project_name,
                'time_label': _format_activity_time(task.created_at),
                'sort_key': task.created_at,
            })
        elif assignee:
            activities.append({
                'icon': 'bi-person-check-fill',
                'color': 'primary',
                'message': f'Task <strong>{task.title}</strong> assigned to {assignee}',
                'detail': project_name,
                'time_label': _format_activity_time(task.created_at),
                'sort_key': task.created_at,
            })
        elif task.status == 'In Progress':
            activities.append({
                'icon': 'bi-lightning-charge-fill',
                'color': 'warning',
                'message': f'<strong>{task.title}</strong> moved to In Progress',
                'detail': project_name,
                'time_label': _format_activity_time(task.created_at),
                'sort_key': task.created_at,
            })
        else:
            activities.append({
                'icon': 'bi-plus-circle-fill',
                'color': 'info',
                'message': f'New task <strong>{task.title}</strong> created',
                'detail': project_name,
                'time_label': _format_activity_time(task.created_at),
                'sort_key': task.created_at,
            })

    activities.sort(key=lambda x: x['sort_key'], reverse=True)
    return activities[:limit]


@dashboard_bp.route('/')
@login_required
def index():
    """Display main dashboard with role-based statistics."""
    all_tasks = current_user.get_dashboard_tasks()
    all_projects = current_user.get_dashboard_projects()
    
    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for task in all_tasks if task.status == 'Completed')
    pending_tasks = sum(1 for task in all_tasks if task.status == 'Pending')
    in_progress_tasks = sum(1 for task in all_tasks if task.status == 'In Progress')
    overdue_tasks = sum(1 for task in all_tasks if task.is_overdue())
    
    completion_percentage = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
    
    recent_tasks = sorted(all_tasks, key=lambda x: x.created_at, reverse=True)[:5]
    
    today = datetime.utcnow().date()
    upcoming_tasks = [task for task in all_tasks 
                     if task.due_date and task.due_date >= today and task.status != 'Completed']
    upcoming_tasks = sorted(upcoming_tasks, key=lambda x: x.due_date)[:5]
    
    overdue_task_list = [task for task in all_tasks if task.is_overdue()]
    
    total_projects = len(all_projects)
    project_stats = []
    for project in all_projects:
        if current_user.is_admin():
            project_tasks = project.tasks
        else:
            project_tasks = [t for t in project.tasks if t.assigned_to == current_user.id]
        project_completed = sum(1 for t in project_tasks if t.status == 'Completed')
        project_total = len(project_tasks)
        project_percentage = round((project_completed / project_total * 100) if project_total > 0 else 0, 1)
        
        project_stats.append({
            'name': project.name,
            'total': project_total,
            'completed': project_completed,
            'percentage': project_percentage
        })
    
    project_stats = sorted(project_stats, key=lambda x: x['percentage'], reverse=True)

    priority_low = sum(1 for t in all_tasks if t.priority == 'Low')
    priority_medium = sum(1 for t in all_tasks if t.priority == 'Medium')
    priority_high = sum(1 for t in all_tasks if t.priority == 'High')

    activity_feed = build_activity_feed(all_tasks)
    chart_data = {
        'statusLabels': ['Completed', 'In Progress', 'Pending', 'Overdue'],
        'statusValues': [completed_tasks, in_progress_tasks, pending_tasks, overdue_tasks],
        'priorityLabels': ['Low', 'Medium', 'High'],
        'priorityValues': [priority_low, priority_medium, priority_high],
        'completionPercentage': completion_percentage,
    }
    
    return render_template('dashboard.html',
                          total_tasks=total_tasks,
                          completed_tasks=completed_tasks,
                          pending_tasks=pending_tasks,
                          in_progress_tasks=in_progress_tasks,
                          overdue_tasks=overdue_tasks,
                          completion_percentage=completion_percentage,
                          recent_tasks=recent_tasks,
                          upcoming_tasks=upcoming_tasks,
                          overdue_task_list=overdue_task_list,
                          total_projects=total_projects,
                          project_stats=project_stats,
                          is_member_view=current_user.is_member(),
                          activity_feed=activity_feed,
                          chart_data=chart_data)
