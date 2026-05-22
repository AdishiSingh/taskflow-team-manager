"""
Main Flask application for Team Task Manager.
Initializes the app, database, and registers all blueprints.
"""

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager
from config import get_config
from models import db, User
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = get_config()
app.config.from_object(config)

# Initialize database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'


@login_manager.unauthorized_handler
def unauthorized():
    """Return JSON for API routes; redirect browser users to login."""
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Authentication required. Please log in first.',
        }), 401
    return redirect(url_for('auth.login', next=request.url))


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


# Register blueprints
from routes.auth import auth_bp
from routes.project import project_bp
from routes.task import task_bp
from routes.dashboard import dashboard_bp
from routes.api import api_bp

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(project_bp, url_prefix='/project')
app.register_blueprint(task_bp, url_prefix='/task')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(api_bp, url_prefix='/api')


# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 Not Found errors."""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Resource not found'}), 404
    return render_template('error.html', error_code=404, 
                          error_message='Page not found'), 404


@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 Forbidden errors."""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    return render_template(
        'error.html',
        error_code=403,
        error_message='Access Denied',
        error_detail='You do not have permission to perform this action. '
                     'Contact an administrator if you need access.'
    ), 403


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    db.session.rollback()
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
    return render_template('error.html', error_code=500, 
                          error_message='Internal server error'), 500


# Root route
@app.route('/')
def index():
    """Redirect to dashboard if logged in, otherwise to login."""
    from flask_login import current_user
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('index.html')


# Context processor to make current date available in all templates
@app.context_processor
def inject_globals():
    """Inject shared template variables."""
    from flask_login import current_user
    return {
        'now': datetime.utcnow(),
        'is_admin': current_user.is_authenticated and current_user.is_admin(),
    }


# Create database tables
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001, use_reloader=False)
