import os
from flask import Flask, render_template
from config import Config
from extensions import db, login_manager

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register Blueprints
    from modules.auth.routes import auth_bp
    from modules.dashboard.routes import dashboard_bp
    from modules.student.routes import student_bp
    from modules.skills.routes import skills_bp
    from modules.companies.routes import companies_bp
    from modules.skill_gap.routes import skill_gap_bp
    from modules.study_planner.routes import study_planner_bp
    from modules.projects.routes import projects_bp
    from modules.coding.routes import coding_bp
    from modules.interviews.routes import interviews_bp
    from modules.resume.routes import resume_bp
    from modules.analytics.routes import analytics_bp
    from modules.notifications.routes import notifications_bp
    from modules.faculty.routes import faculty_bp
    from modules.admin.routes import admin_bp
    from modules.drives.routes import drives_bp
    from modules.games.routes import games_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(skill_gap_bp)
    app.register_blueprint(study_planner_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(coding_bp)
    app.register_blueprint(interviews_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(faculty_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(drives_bp)
    app.register_blueprint(games_bp)

    # Context processors for navbar & active badges
    @app.context_processor
    def inject_global_data():
        from flask_login import current_user
        from models.notification import Notification
        unread_count = 0
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return dict(unread_notifications_count=unread_count)

    # Error handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('components/error.html', code=403, title="Access Forbidden", message="You do not have permission to access this resource or assigned portal."), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('components/error.html', code=404, title="Page Not Found", message="The requested page could not be located on Student Pulse."), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('components/error.html', code=500, title="Server Error", message="An unexpected error occurred. Please try again later."), 500

    return app

# Expose WSGI application for production web servers (e.g. Gunicorn on Render)
app = create_app()

with app.app_context():
    db.create_all()
    # Auto-seed if database is empty upon cloud deployment
    try:
        from models.user import User
        if not User.query.first():
            from seed_official import seed_official_database
            seed_official_database()
    except Exception as e:
        print("Startup verification notice:", e)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Student Pulse on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
