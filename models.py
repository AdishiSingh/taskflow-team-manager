"""
Database models for Team Task Manager application.
Defines User, Project, and Task models with SQLAlchemy relationships.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize SQLAlchemy
db = SQLAlchemy()

# Association table for many-to-many relationship between Users and Projects
project_members = db.Table('project_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    """User model for authentication and authorization."""
    
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='member', nullable=False)  # admin or member
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    # Projects created by this user
    created_projects = db.relationship('Project', backref='creator', lazy=True, 
                                      foreign_keys='Project.created_by')
    
    # Tasks assigned to this user
    assigned_tasks = db.relationship('Task', backref='assigned_user', lazy=True,
                                     foreign_keys='Task.assigned_to')
    
    # Projects this user is a member of (many-to-many)
    member_projects = db.relationship('Project', secondary=project_members,
                                      lazy='subquery',
                                      backref=db.backref('members', lazy=True))
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if the user has admin role."""
        return self.role == 'admin'

    def is_member(self):
        """Check if the user has member role."""
        return self.role == 'member'

    def get_member_project_ids(self):
        """IDs of projects this user belongs to."""
        return {p.id for p in self.member_projects}

    def can_access_project(self, project):
        """Admins access all projects; members only assigned projects."""
        if self.is_admin():
            return True
        return project.id in self.get_member_project_ids()

    def can_update_task_status(self, task):
        """Admins or assignee may update task status."""
        if self.is_admin():
            return True
        if not self.can_access_project(task.project):
            return False
        return task.assigned_to == self.id

    def can_edit_task(self, task):
        """Only admins may edit or delete tasks."""
        return self.is_admin()

    def get_accessible_projects(self):
        """Projects visible in list/dashboard for this user."""
        from models import Project
        if self.is_admin():
            return Project.query.order_by(Project.name.asc()).all()
        return sorted(self.member_projects, key=lambda p: p.name)

    def get_dashboard_tasks(self):
        """Tasks shown on member dashboard (assigned to this user)."""
        if self.is_admin():
            return Task.query.all()
        return Task.query.filter_by(assigned_to=self.id).all()

    def get_dashboard_projects(self):
        """Projects shown on dashboard for this user."""
        return self.get_accessible_projects()
    
    def __repr__(self):
        return f'<User {self.name} ({self.email})>'


class Project(db.Model):
    """Project model for organizing tasks."""
    
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    # Tasks belonging to this project
    tasks = db.relationship('Task', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def get_completion_percentage(self):
        """Calculate the percentage of completed tasks in this project."""
        if not self.tasks:
            return 0
        completed = sum(1 for task in self.tasks if task.status == 'Completed')
        return round((completed / len(self.tasks)) * 100, 1)
    
    def get_task_count_by_status(self):
        """Get count of tasks by status."""
        status_counts = {'Pending': 0, 'In Progress': 0, 'Completed': 0}
        for task in self.tasks:
            if task.status in status_counts:
                status_counts[task.status] += 1
        return status_counts

    def get_member_ids(self):
        """Return IDs of users already on this project."""
        rows = db.session.execute(
            db.select(project_members.c.user_id).where(
                project_members.c.project_id == self.id
            )
        ).scalars().all()
        return set(rows)

    def get_available_members(self):
        """
        Registered users who can be added to this project:
        excludes the project creator and existing members.
        """
        exclude_ids = self.get_member_ids() | {self.created_by}
        query = User.query.order_by(User.name.asc())
        if exclude_ids:
            query = query.filter(User.id.notin_(exclude_ids))
        return query.all()
    
    def __repr__(self):
        return f'<Project {self.name}>'


class Task(db.Model):
    """Task model for tracking work items."""
    
    __tablename__ = 'task'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending', nullable=False)  # Pending, In Progress, Completed
    priority = db.Column(db.String(20), default='Medium', nullable=False)  # Low, Medium, High
    due_date = db.Column(db.Date, nullable=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def is_overdue(self):
        """Check if the task is overdue."""
        if self.due_date and self.status != 'Completed':
            return datetime.utcnow().date() > self.due_date
        return False
    
    def get_priority_color(self):
        """Return Bootstrap color class based on priority."""
        priority_colors = {
            'Low': 'success',
            'Medium': 'warning',
            'High': 'danger'
        }
        return priority_colors.get(self.priority, 'secondary')
    
    def get_status_color(self):
        """Return Bootstrap color class based on status."""
        status_colors = {
            'Pending': 'secondary',
            'In Progress': 'primary',
            'Completed': 'success'
        }
        return status_colors.get(self.status, 'secondary')
    
    def __repr__(self):
        return f'<Task {self.title}>'
