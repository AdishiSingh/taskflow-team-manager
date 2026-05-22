"""
Task management routes for Team Task Manager.
Handles task CRUD operations, status updates, and assignments.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, Project, Task
from datetime import datetime
from permissions import admin_required, member_project_access_required

task_bp = Blueprint('task', __name__)


@task_bp.route('/create/<int:project_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def create(project_id):
    """Create a new task in a project (admin only)."""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'Pending')
        priority = request.form.get('priority', 'Medium')
        due_date = request.form.get('due_date')
        assigned_to = request.form.get('assigned_to')
        
        if not title:
            flash('Task title is required.', 'danger')
            return render_template('create_task.html', project=project, 
                                  title=title, description=description, 
                                  status=status, priority=priority, due_date=due_date,
                                  members=project.members)
        
        due_date_obj = None
        if due_date:
            try:
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
                return render_template('create_task.html', project=project,
                                      title=title, description=description,
                                      status=status, priority=priority, due_date=due_date,
                                      members=project.members)
        
        assigned_user_id = int(assigned_to) if assigned_to else None
        if assigned_user_id and assigned_user_id not in project.get_member_ids():
            flash('Tasks can only be assigned to project members.', 'danger')
            return render_template('create_task.html', project=project,
                                  title=title, description=description,
                                  status=status, priority=priority, due_date=due_date,
                                  members=project.members)

        task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date_obj,
            project_id=project_id,
            assigned_to=assigned_user_id
        )
        
        try:
            db.session.add(task)
            db.session.commit()
            flash('Task created successfully!', 'success')
            return redirect(url_for('project.detail', project_id=project_id))
        except Exception:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            return render_template('create_task.html', project=project,
                                  title=title, description=description,
                                  status=status, priority=priority, due_date=due_date,
                                  members=project.members)
    
    return render_template('create_task.html', project=project, members=project.members)


@task_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(task_id):
    """Edit task details (admin only)."""
    task = Task.query.get_or_404(task_id)
    project = task.project
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'Pending')
        priority = request.form.get('priority', 'Medium')
        due_date = request.form.get('due_date')
        assigned_to = request.form.get('assigned_to')
        
        if not title:
            flash('Task title is required.', 'danger')
            return render_template('edit_task.html', task=task, project=project,
                                  members=project.members)
        
        due_date_obj = None
        if due_date:
            try:
                due_date_obj = datetime.strptime(due_date, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
                return render_template('edit_task.html', task=task, project=project,
                                      members=project.members)
        
        assigned_user_id = int(assigned_to) if assigned_to else None
        if assigned_user_id and assigned_user_id not in project.get_member_ids():
            flash('Tasks can only be assigned to project members.', 'danger')
            return render_template('edit_task.html', task=task, project=project,
                                  members=project.members)

        task.title = title
        task.description = description
        task.status = status
        task.priority = priority
        task.due_date = due_date_obj
        task.assigned_to = assigned_user_id
        
        try:
            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('project.detail', project_id=project.id))
        except Exception:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            return render_template('edit_task.html', task=task, project=project,
                                  members=project.members)
    
    return render_template('edit_task.html', task=task, project=project, members=project.members)


@task_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(task_id):
    """Delete a task (admin only)."""
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id
    
    try:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
        return redirect(url_for('project.detail', project_id=project_id))
    except Exception:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('project.detail', project_id=project_id))


@task_bp.route('/<int:task_id>/update_status', methods=['POST'])
@login_required
def update_status(task_id):
    """Update task status: admins any task; members only their assigned tasks."""
    task = Task.query.get_or_404(task_id)
    project = task.project

    if not current_user.can_update_task_status(task):
        abort(403)
    
    new_status = request.form.get('status')
    
    if new_status not in ['Pending', 'In Progress', 'Completed']:
        flash('Invalid status.', 'danger')
        return redirect(url_for('project.detail', project_id=project.id))
    
    task.status = new_status
    
    try:
        db.session.commit()
        flash('Task status updated successfully!', 'success')
        return redirect(url_for('project.detail', project_id=project.id))
    except Exception:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('project.detail', project_id=project.id))
