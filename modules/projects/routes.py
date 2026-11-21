from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime, date
from extensions import db
from models.project import StudentProject, ProjectMilestone
from services.activity_service import log_activity
from services.notification_service import send_notification
from models.academic import FacultyStudentAssignment

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

@projects_bp.route('/')
@login_required
def index():
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile
    projects = profile.projects.order_by(StudentProject.created_at.desc()).all()
    return render_template('projects/index.html', projects=projects)


@projects_bp.route('/add', methods=['POST'])
@login_required
def add():
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile

    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    category = request.form.get('category', 'Academic')
    tech_stack = request.form.get('tech_stack', '').strip()
    github_url = request.form.get('github_url', '').strip()
    live_url = request.form.get('live_url', '').strip()
    progress_percentage = int(request.form.get('progress_percentage', 20))

    project = StudentProject(
        student_id=profile.id,
        title=title,
        description=description,
        category=category,
        tech_stack=tech_stack,
        github_url=github_url,
        live_url=live_url,
        progress_percentage=progress_percentage,
        status='In Progress' if progress_percentage < 100 else 'Completed'
    )
    db.session.add(project)
    db.session.flush()

    # Add default milestone
    m1 = ProjectMilestone(
        project_id=project.id,
        title="Project Initialization & Architecture Setup",
        description="Repository initialized, core stack configured.",
        is_completed=True,
        completed_at=datetime.utcnow()
    )
    db.session.add(m1)
    db.session.commit()

    log_activity(
        student_id=profile.id,
        activity_type='project_milestone',
        activity_title=f"Initialized Project: {title}",
        duration_minutes=45,
        related_record_id=project.id
    )

    flash(f'Project "{title}" created successfully!', 'success')
    return redirect(url_for('projects.index'))


@projects_bp.route('/update-milestone/<int:milestone_id>', methods=['POST'])
@login_required
def update_milestone(milestone_id):
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile
    m = ProjectMilestone.query.get_or_404(milestone_id)
    if m.project.student_id != profile.id:
        abort(403)

    m.is_completed = not m.is_completed
    if m.is_completed:
        m.completed_at = datetime.utcnow()
        log_activity(
            student_id=profile.id,
            activity_type='project_milestone',
            activity_title=f"Completed Milestone: {m.title}",
            duration_minutes=45,
            related_record_id=m.id
        )
        flash(f'Milestone "{m.title}" marked as complete! Streak updated.', 'success')
    else:
        m.completed_at = None
        flash('Milestone marked as pending.', 'info')

    # Recalculate project progress
    total_m = m.project.milestones.count()
    if total_m > 0:
        done_m = m.project.milestones.filter_by(is_completed=True).count()
        m.project.progress_percentage = int((done_m / total_m) * 100)
        if m.project.progress_percentage == 100:
            m.project.status = 'Completed'

    db.session.commit()
    return redirect(url_for('projects.index'))


@projects_bp.route('/submit-review/<int:project_id>', methods=['POST'])
@login_required
def submit_review(project_id):
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile
    project = StudentProject.query.filter_by(id=project_id, student_id=profile.id).first_or_404()

    project.submitted_for_review = True
    project.status = 'Under Review'
    db.session.commit()

    # Notify assigned faculty
    assignment = FacultyStudentAssignment.query.filter_by(student_id=profile.id).first()
    if assignment:
        send_notification(
            user_id=assignment.faculty.user_id,
            title=f"Project Review Submitted: {project.title}",
            message=f"Student {profile.user.full_name} submitted '{project.title}' for your review.",
            category='info',
            link=url_for('faculty.student_detail', student_id=profile.id)
        )

    flash(f'Project "{project.title}" has been submitted for faculty mentorship review!', 'success')
    return redirect(url_for('projects.index'))
