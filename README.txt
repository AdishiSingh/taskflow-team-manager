================================================================================
                    TEAM TASK MANAGER - README
================================================================================

PROJECT OVERVIEW
----------------
Team Task Manager is a production-ready, full-stack web application for 
collaborative project and task management. It enables teams to organize work,
track progress, and manage tasks efficiently with role-based access control.

Built with Flask, PostgreSQL, and Bootstrap 5, this application is designed
for deployment on Railway and is suitable for professional use.


FEATURES
--------
User Management:
- User registration with email validation
- Secure password hashing using Werkzeug
- Role-based access control (Admin/Member)
- Session management with Flask-Login

Project Management:
- Create, edit, and delete projects (Admin only)
- Add/remove team members to projects
- View project statistics and progress
- Track project completion percentage

Task Management:
- Create, edit, and delete tasks
- Assign tasks to team members
- Set task priorities (Low, Medium, High)
- Track task status (Pending, In Progress, Completed)
- Set due dates with overdue detection
- Update task status (Admins and assigned users)

Dashboard:
- Real-time statistics (Total, Completed, Pending, Overdue tasks)
- Overall progress tracking with visual progress bars
- Recent tasks overview
- Upcoming deadlines display
- Project progress statistics
- Overdue task alerts

Security:
- Password hashing with Werkzeug
- Session protection
- Role-based access control
- SQL injection protection via SQLAlchemy
- CSRF protection ready


TECH STACK
----------
Backend:
- Python 3.x
- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Flask-Login 0.6.3
- Werkzeug 3.0.1
- python-dotenv 1.0.0
- Gunicorn 21.2.0

Frontend:
- HTML5
- CSS3
- Bootstrap 5.3.0
- Bootstrap Icons
- JavaScript (ES6+)

Database:
- PostgreSQL

Deployment:
- Railway compatible
- Gunicorn WSGI server


FOLDER STRUCTURE
----------------
team-task-manager/
│
├── app.py                    # Main Flask application
├── config.py                 # Configuration management
├── models.py                 # SQLAlchemy database models
├── requirements.txt          # Python dependencies
├── Procfile                  # Railway deployment configuration
├── README.txt                # This file
│
├── routes/                   # Application routes (Blueprints)
│   ├── auth.py              # Authentication routes
│   ├── project.py           # Project management routes
│   ├── task.py              # Task management routes
│   └── dashboard.py         # Dashboard routes
│
├── templates/                # Jinja2 HTML templates
│   ├── base.html            # Base template with navbar
│   ├── index.html           # Landing page
│   ├── login.html           # Login page
│   ├── signup.html          # Registration page
│   ├── dashboard.html       # Dashboard page
│   ├── create_project.html  # Project creation/editing
│   ├── projects.html        # Projects list
│   ├── project_detail.html  # Project details page
│   ├── create_task.html     # Task creation
│   ├── edit_task.html       # Task editing
│   └── error.html           # Error pages (404, 403, 500)
│
├── static/                   # Static assets
│   ├── css/
│   │   └── style.css        # Custom CSS styles
│   └── js/
│       └── script.js        # Custom JavaScript
│
└── instance/                 # Database instance folder


INSTALLATION STEPS
------------------

Prerequisites:
- Python 3.8 or higher
- PostgreSQL installed locally (for development)
- Git (optional, for version control)

Local Setup:

1. Navigate to the project directory:
   cd team-task-manager

2. Create a virtual environment:
   python -m venv venv

3. Activate the virtual environment:
   On Windows:
   venv\Scripts\activate
   
   On macOS/Linux:
   source venv/bin/activate

4. Install dependencies:
   pip install -r requirements.txt

5. Set up PostgreSQL database:
   - Create a new database named "team_task_manager"
   - Note your database credentials

6. Configure environment variables:
   Create a .env file in the project root with:
   
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=postgresql://username:password@localhost:5432/team_task_manager
   FLASK_ENV=development

7. Initialize the database:
   python -c "from app import app; from models import db; app.app_context().push(); db.create_all()"

8. Run the application:
   python app.py

9. Access the application:
   Open your browser and go to: http://localhost:5000


RAILWAY DEPLOYMENT STEPS
------------------------

1. Prepare your code:
   - Ensure all files are committed to Git
   - Verify .env is in .gitignore (don't commit secrets)
   - Ensure Procfile is present in the root

2. Create a Railway account:
   - Go to https://railway.app
   - Sign up or log in

3. Create a new project:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your GitHub repository

4. Add PostgreSQL database:
   - In your Railway project, click "+ New"
   - Select "PostgreSQL"
   - Railway will provide DATABASE_URL automatically

5. Configure environment variables:
   - Go to your project settings
   - Add SECRET_KEY (generate a secure random string)
   - Set FLASK_ENV=production
   - DATABASE_URL is automatically set by Railway

6. Deploy:
   - Railway will automatically deploy on push
   - Monitor deployment logs in the Railway dashboard

7. Access your application:
   - Railway will provide a public URL
   - Your app is now live!


DATABASE INITIALIZATION COMMANDS
---------------------------------

For local development:

1. Start PostgreSQL service:
   On macOS (with Homebrew):
   brew services start postgresql
   
   On Linux:
   sudo service postgresql start
   
   On Windows:
   Start PostgreSQL from Services

2. Create database:
   psql -U postgres
   CREATE DATABASE team_task_manager;
   \q

3. Run database initialization:
   python -c "from app import app; from models import db; app.app_context().push(); db.create_all()"

4. (Optional) Create initial admin user:
   python -c "
   from app import app
   from models import db, User
   app.app_context().push()
   admin = User(name='Admin', email='admin@example.com', role='admin')
   admin.set_password('admin123')
   db.session.add(admin)
   db.session.commit()
   "


GITHUB PUSH COMMANDS
--------------------

1. Initialize Git repository (if not already done):
   git init

2. Add all files:
   git add .

3. Commit changes:
   git commit -m "Initial commit: Team Task Manager application"

4. Create repository on GitHub:
   - Go to https://github.com/new
   - Create a new repository
   - Copy the repository URL

5. Add remote:
   git remote add origin https://github.com/your-username/team-task-manager.git

6. Push to GitHub:
   git branch -M main
   git push -u origin main


DEMO CREDENTIALS
----------------

For testing purposes, you can create the following demo users:

Admin User:
- Email: admin@example.com
- Password: admin123
- Role: Admin (can create projects, manage all tasks)

Member User:
- Email: member@example.com
- Password: member123
- Role: Member (can view assigned projects, update task status)

To create these users, run:

python -c "
from app import app
from models import db, User
app.app_context().push()

# Create admin
admin = User(name='Admin User', email='admin@example.com', role='admin')
admin.set_password('admin123')
db.session.add(admin)

# Create member
member = User(name='Member User', email='member@example.com', role='member')
member.set_password('member123')
db.session.add(member)

db.session.commit()
print('Demo users created successfully!')
"


SCREENSHOTS SECTION
-------------------

[Placeholder for application screenshots]

1. Landing Page - Shows the homepage with feature cards
2. Login Page - User authentication interface
3. Dashboard - Statistics cards, progress bars, task overview
4. Projects List - Grid view of all projects with progress
5. Project Detail - Project info, team members, task table
6. Task Creation - Form for creating new tasks
7. Error Pages - Custom 404, 403, and 500 error pages


TROUBLESHOOTING
---------------

Issue: Database connection error
Solution:
- Verify PostgreSQL is running
- Check DATABASE_URL in .env file
- Ensure database exists

Issue: Module import errors
Solution:
- Ensure virtual environment is activated
- Run: pip install -r requirements.txt

Issue: Port already in use
Solution:
- Change port in app.py (default: 5000)
- Or kill process using port 5000

Issue: Permission denied errors
Solution:
- Ensure proper file permissions
- Run with appropriate user permissions


SECURITY NOTES
---------------

1. Change SECRET_KEY in production
2. Use strong passwords for database
3. Enable HTTPS in production
4. Keep dependencies updated
5. Never commit .env file to version control
6. Use environment variables for sensitive data


CONTACT & SUPPORT
-----------------

For issues, questions, or contributions:
- GitHub Issues: [Your Repository URL]
- Email: [Your Email]


LICENSE
-------

This project is provided as-is for educational and professional use.


================================================================================
                        END OF README
================================================================================
