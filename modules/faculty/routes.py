from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from extensions import db
from models.user import StudentProfile, FacultyProfile
from models.academic import Batch, FacultyBatchAssignment, FacultyStudentAssignment
from models.study_plan import StudyTask
from models.project import StudentProject, ProjectReview
from models.faculty import FacultyFeedback, MentorshipTarget, MentorshipSession
from models.activity import StudentActivityLog
from services.activity_service import get_heatmap_data
from services.notification_service import send_notification

faculty_bp = Blueprint('faculty', __name__, url_prefix='/faculty')

@faculty_bp.before_request
@login_required
def check_faculty_role():
    if not current_user.is_faculty() and not current_user.is_admin():
        abort(403)

def get_authorized_student_ids(faculty_prof_id):
    """Returns set of student_ids assigned to this faculty via batch or direct assignment."""
    if current_user.is_admin():
        return set(s.id for s in StudentProfile.query.all())

    # Direct student assignments
    direct = db.session.query(FacultyStudentAssignment.student_id).filter_by(faculty_id=faculty_prof_id).all()
    student_ids = set(d[0] for d in direct)

    # Batch assignments
    batch_assigns = FacultyBatchAssignment.query.filter_by(faculty_id=faculty_prof_id).all()
    for ba in batch_assigns:
        for sa in ba.batch.student_assignments:
            student_ids.add(sa.student_id)

    return student_ids


@faculty_bp.route('/dashboard')
def dashboard():
    profile = current_user.faculty_profile
    if not profile and not current_user.is_admin():
        flash('Faculty profile not configured.', 'danger')
        return redirect(url_for('auth.logout'))

    fac_id = profile.id if profile else 0
    auth_student_ids = get_authorized_student_ids(fac_id)

    students = StudentProfile.query.filter(StudentProfile.id.in_(auth_student_ids)).all() if auth_student_ids else []
    total_assigned = len(students)

    # Calculate at-risk students (no activity in 7 days or low assessment pass rate)
    seven_days_ago = date.today() - timedelta(days=7)
    active_count = 0
    at_risk_students = []

    for s in students:
        has_recent = StudentActivityLog.query.filter(
            StudentActivityLog.student_id == s.id,
            StudentActivityLog.activity_date >= seven_days_ago
        ).first()

        total_att = s.assessment_attempts.count()
        passed_att = s.assessment_attempts.filter_by(passed=True).count()
        pass_rate = int((passed_att / total_att * 100)) if total_att > 0 else 100

        if has_recent:
            active_count += 1
        else:
            at_risk_students.append({
                'student': s,
                'reason': 'No learning activity recorded in past 7 days'
            })
        if pass_rate < 50 and total_att >= 2:
            if s not in [item['student'] for item in at_risk_students]:
                at_risk_students.append({
                    'student': s,
                    'reason': f'Low assessment pass rate ({pass_rate}%)'
                })

    inactive_count = total_assigned - active_count

    # Pending project reviews
    pending_projects = StudentProject.query.filter(
        StudentProject.student_id.in_(auth_student_ids),
        StudentProject.submitted_for_review == True,
        StudentProject.status == 'Under Review'
    ).all() if auth_student_ids else []

    # Recent feedback sent
    recent_feedbacks = profile.feedbacks_given.order_by(FacultyFeedback.created_at.desc()).limit(5).all() if profile else []

    return render_template(
        'faculty/dashboard.html',
        profile=profile,
        students=students,
        total_assigned=total_assigned,
        active_count=active_count,
        inactive_count=inactive_count,
        at_risk_students=at_risk_students,
        pending_projects=pending_projects,
        recent_feedbacks=recent_feedbacks
    )


@faculty_bp.route('/quick-log-prep/<int:student_id>', methods=['POST', 'GET'])
def quick_log_prep(student_id):
    """Demo helper: logs activity today for student so faculty can see live status shift from At-Risk to Actively Preparing."""
    today = date.today()
    log = StudentActivityLog(
        student_id=student_id,
        activity_type='study_task',
        activity_title='Completed Diagnostic Mock Test & Study Session',
        activity_date=today,
        duration_minutes=60,
        status='completed'
    )
    db.session.add(log)
    db.session.commit()
    flash('Recent 7-day learning activity logged for student! Status updated to "Actively Preparing".', 'success')
    return redirect(url_for('faculty.dashboard'))


@faculty_bp.route('/students')
def students_list():
    profile = current_user.faculty_profile
    fac_id = profile.id if profile else 0
    auth_student_ids = get_authorized_student_ids(fac_id)

    search = request.args.get('q', '').strip()
    dept_filter = request.args.get('department', 'all')

    query = StudentProfile.query.filter(StudentProfile.id.in_(auth_student_ids)) if auth_student_ids else StudentProfile.query.filter_by(id=-1)

    if dept_filter != 'all':
        query = query.filter_by(department=dept_filter)

    students = query.all()
    if search:
        students = [s for s in students if search.lower() in s.user.full_name.lower() or search.lower() in s.enrollment_number.lower()]

    return render_template('faculty/students.html', students=students, search=search, dept_filter=dept_filter)


@faculty_bp.route('/student/<int:student_id>')
def student_detail(student_id):
    profile = current_user.faculty_profile
    fac_id = profile.id if profile else 0
    auth_student_ids = get_authorized_student_ids(fac_id)

    if student_id not in auth_student_ids:
        flash('Unauthorized: You can only view students assigned to your mentorship batches.', 'danger')
        abort(403)

    student = StudentProfile.query.get_or_404(student_id)
    year = request.args.get('year', type=int) or date.today().year
    heatmap = get_heatmap_data(student.id, year=year)

    tasks = StudyTask.query.filter_by(student_id=student.id).all()
    completed_tasks = sum(1 for t in tasks if t.is_completed)
    study_plan_progress = int((completed_tasks / len(tasks) * 100)) if tasks else 0

    return render_template(
        'faculty/student_detail.html',
        student=student,
        heatmap=heatmap,
        study_plan_progress=study_plan_progress,
        tasks=tasks[:10],
        projects=student.projects.all(),
        feedbacks=student.feedback_received.order_by(FacultyFeedback.created_at.desc()).all(),
        targets=student.mentorship_targets.order_by(MentorshipTarget.created_at.desc()).all()
    )


@faculty_bp.route('/give-feedback/<int:student_id>', methods=['POST'])
def give_feedback(student_id):
    profile = current_user.faculty_profile
    fac_id = profile.id if profile else 0
    auth_student_ids = get_authorized_student_ids(fac_id)

    if student_id not in auth_student_ids:
        abort(403)

    student = StudentProfile.query.get_or_404(student_id)
    text = request.form.get('feedback_text', '').strip()
    category = request.form.get('category', 'Skill Improvement')
    is_at_risk = bool(request.form.get('is_at_risk_alert'))

    feedback = FacultyFeedback(
        faculty_id=profile.id,
        student_id=student.id,
        feedback_text=text,
        category=category,
        is_at_risk_alert=is_at_risk
    )
    db.session.add(feedback)
    db.session.commit()

    send_notification(
        user_id=student.user_id,
        title=f"New Faculty Mentorship Feedback ({category})",
        message=f"{current_user.full_name}: {text}",
        category='warning' if is_at_risk else 'info',
        link=url_for('student.dashboard')
    )

    flash('Mentorship feedback recorded and student notified.', 'success')
    return redirect(url_for('faculty.student_detail', student_id=student.id))


@faculty_bp.route('/assign-target/<int:student_id>', methods=['POST'])
def assign_target(student_id):
    profile = current_user.faculty_profile
    fac_id = profile.id if profile else 0
    auth_student_ids = get_authorized_student_ids(fac_id)

    if student_id not in auth_student_ids:
        abort(403)

    student = StudentProfile.query.get_or_404(student_id)
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    target_skill = request.form.get('target_skill', 'Core')
    deadline_str = request.form.get('deadline')
    deadline = date.fromisoformat(deadline_str) if deadline_str else date.today() + timedelta(days=7)

    target = MentorshipTarget(
        faculty_id=profile.id,
        student_id=student.id,
        title=title,
        description=description,
        target_skill=target_skill,
        deadline=deadline,
        status='Pending'
    )
    db.session.add(target)
    db.session.commit()

    send_notification(
        user_id=student.user_id,
        title=f"New Learning Target Assigned: {title}",
        message=f"Prof. {current_user.last_name} assigned target '{title}' due on {deadline}.",
        category='info',
        link=url_for('student.dashboard')
    )

    flash(f'Target "{title}" assigned to {student.user.full_name}.', 'success')
    return redirect(url_for('faculty.student_detail', student_id=student.id))


@faculty_bp.route('/review-project/<int:project_id>', methods=['POST'])
def review_project(project_id):
    profile = current_user.faculty_profile
    project = StudentProject.query.get_or_404(project_id)
    auth_student_ids = get_authorized_student_ids(profile.id if profile else 0)

    if project.student_id not in auth_student_ids:
        abort(403)

    feedback_text = request.form.get('feedback', '').strip()
    rating = int(request.form.get('rating', 4))
    grade = request.form.get('grade', 'A')

    review = ProjectReview(
        project_id=project.id,
        faculty_id=profile.id,
        feedback=feedback_text,
        rating=rating,
        grade=grade
    )
    db.session.add(review)

    project.status = 'Completed' if rating >= 4 else 'In Progress'
    project.submitted_for_review = False
    db.session.commit()

    send_notification(
        user_id=project.student_profile.user_id,
        title=f"Project Review Completed: {project.title}",
        message=f"Prof. {current_user.last_name} evaluated your project. Grade: {grade}, Rating: {rating}/5.",
        category='success',
        link=url_for('projects.index')
    )

    flash(f'Project "{project.title}" review submitted.', 'success')
    return redirect(url_for('faculty.student_detail', student_id=project.student_id))
