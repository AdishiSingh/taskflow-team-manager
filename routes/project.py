"""
Project management routes for Team Task Manager.
Handles project CRUD operations and member management.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, User, Project
from permissions import admin_required, member_project_access_required

project_bp = Blueprint('project', __name__)


@project_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Create a new project (admin only)."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Project name is required.', 'danger')
            return render_template('create_project.html', name=name, description=description)
        
        project = Project(name=name, description=description, created_by=current_user.id)
        
        try:
            db.session.add(project)
            db.session.commit()
            project.members.append(current_user)
            db.session.commit()
            flash('Project created successfully!', 'success')
            return redirect(url_for('project.detail', project_id=project.id))
        except Exception:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            return render_template('create_project.html', name=name, description=description)
    
    return render_template('create_project.html')


@project_bp.route('/')
@login_required
def list():
    """List projects: all for admins, assigned only for members."""
    projects = current_user.get_accessible_projects()
    return render_template('projects.html', projects=projects)


@project_bp.route('/<int:project_id>')
@login_required
@member_project_access_required
def detail(project_id):
    """View project details."""
    project = Project.query.get_or_404(project_id)
    tasks = project.tasks
    members = project.members
    available_users = project.get_available_members() if current_user.is_admin() else []
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == 'Completed')
    pending_tasks = sum(1 for task in tasks if task.status == 'Pending')
    in_progress_tasks = sum(1 for task in tasks if task.status == 'In Progress')
    overdue_tasks = sum(1 for task in tasks if task.is_overdue())
    
    return render_template('project_detail.html', 
                          project=project, 
                          tasks=tasks, 
                          members=members,
                          available_users=available_users,
                          total_tasks=total_tasks,
                          completed_tasks=completed_tasks,
                          pending_tasks=pending_tasks,
                          in_progress_tasks=in_progress_tasks,
                          overdue_tasks=overdue_tasks)


@project_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(project_id):
    """Edit project details (admin only)."""
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Project name is required.', 'danger')
            return render_template('create_project.html', project=project, name=name, description=description)
        
        project.name = name
        project.description = description
        
        try:
            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('project.detail', project_id=project.id))
        except Exception:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
            return render_template('create_project.html', project=project, name=name, description=description)
    
    return render_template('create_project.html', project=project, name=project.name, description=project.description)


@project_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(project_id):
    """Delete project (admin only)."""
    project = Project.query.get_or_404(project_id)
    
    try:
        db.session.delete(project)
        db.session.commit()
        flash('Project deleted successfully!', 'success')
        return redirect(url_for('project.list'))
    except Exception:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('project.detail', project_id=project.id))


@project_bp.route('/<int:project_id>/add_member', methods=['POST'])
@login_required
@admin_required
def add_member(project_id):
    """Add a member to the project (admin only)."""
    project = Project.query.get_or_404(project_id)
    user_id = request.form.get('user_id', type=int)
    
    if not user_id:
        flash('Please select a user to add.', 'warning')
        return redirect(url_for('project.detail', project_id=project_id))
    
    user = db.session.get(User, user_id)
    
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('project.detail', project_id=project_id))

    if user.id == project.created_by:
        flash('The project creator is already part of this team.', 'info')
        return redirect(url_for('project.detail', project_id=project_id))

    if user.id in project.get_member_ids():
        flash(f'{user.name} is already a member of this project.', 'warning')
        return redirect(url_for('project.detail', project_id=project_id))

    allowed_ids = {u.id for u in project.get_available_members()}
    if user.id not in allowed_ids:
        flash('This user cannot be added to the project.', 'danger')
        return redirect(url_for('project.detail', project_id=project_id))
    
    try:
        project.members.append(user)
        db.session.commit()
        flash(f'{user.name} has been added to the project!', 'success')
        return redirect(url_for('project.detail', project_id=project_id))
    except Exception:
        db.session.rollback()
        flash('An error occurred while adding the member. Please try again.', 'danger')
        return redirect(url_for('project.detail', project_id=project_id))


@project_bp.route('/<int:project_id>/remove_member/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def remove_member(project_id, user_id):
    """Remove a member from the project (admin only)."""
    project = Project.query.get_or_404(project_id)
    user = User.query.get_or_404(user_id)
    
    if user not in project.members:
        flash('User is not a member of this project.', 'warning')
        return redirect(url_for('project.detail', project_id=project_id))
    
    if user.id == project.created_by:
        flash('Cannot remove the project creator.', 'danger')
        return redirect(url_for('project.detail', project_id=project_id))
    
    try:
        project.members.remove(user)
        db.session.commit()
        flash(f'{user.name} removed from the project.', 'success')
        return redirect(url_for('project.detail', project_id=project_id))
    except Exception:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')
        return redirect(url_for('project.detail', project_id=project_id))
