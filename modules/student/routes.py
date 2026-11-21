from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from extensions import db
from models.user import StudentProfile
from models.skill import StudentSkill
from models.study_plan import StudyPlan, StudyTask
from models.project import StudentProject
from models.assessment import AssessmentAttempt
from models.faculty import FacultyFeedback, MentorshipTarget
from models.activity import StudentActivityLog
from services.activity_service import get_heatmap_data, log_activity
from services.streak_service import update_student_streak

student_bp = Blueprint('student', __name__, url_prefix='/student')

@student_bp.before_request
@login_required
def check_student_role():
    if not current_user.is_student() and not current_user.is_admin():
        abort(403)

@student_bp.route('/dashboard')
def dashboard():
    profile = current_user.student_profile
    if not profile:
        flash('Student profile not found. Please contact administration.', 'danger')
        return redirect(url_for('auth.logout'))

    # Recalculate streak to ensure real-time accuracy
    update_student_streak(profile.id)

    # 1. Skills stats
    skills = profile.skills.all()
    total_skills = len(skills)
    learning_skills = sum(1 for s in skills if s.learning_status == 'Learning')
    mastered_skills = sum(1 for s in skills if s.proficiency in ('Advanced', 'Expert'))
    avg_proficiency = int(sum(s.numeric_proficiency() for s in skills) / total_skills) if total_skills > 0 else 0

    # 2. Study Plan stats
    active_plans = profile.study_plans.filter_by(status='Active').all()
    all_tasks = StudyTask.query.filter_by(student_id=profile.id).all()
    total_tasks = len(all_tasks)
    completed_tasks = sum(1 for t in all_tasks if t.is_completed)
    study_plan_completion = int((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

    # Upcoming tasks (pending, due soon)
    upcoming_tasks = StudyTask.query.filter_by(student_id=profile.id, is_completed=False)\
        .order_by(StudyTask.scheduled_date.asc())\
        .limit(5).all()

    # 3. Projects stats
    projects = profile.projects.all()
    active_projects = sum(1 for p in projects if p.status in ('In Progress', 'Under Review'))
    completed_projects = sum(1 for p in projects if p.status == 'Completed')

    # 4. Coding & Assessments stats
    attempts = profile.assessment_attempts.all()
    total_quizzes = len(attempts)
    passed_quizzes = sum(1 for a in attempts if a.passed)
    avg_score = int(sum(a.score for a in attempts) / total_quizzes) if total_quizzes > 0 else 0

    # 5. Activity Heatmap & Streaks (LeetCode / GitHub style)
    year = request.args.get('year', type=int) or date.today().year
    heatmap = get_heatmap_data(profile.id, year=year)

    # Weekly learning hours calculation (past 7 days)
    seven_days_ago = date.today() - timedelta(days=7)
    recent_logs = StudentActivityLog.query.filter(
        StudentActivityLog.student_id == profile.id,
        StudentActivityLog.activity_date >= seven_days_ago,
        StudentActivityLog.status == 'completed'
    ).all()
    weekly_minutes = sum(l.duration_minutes for l in recent_logs)
    weekly_hours = round(weekly_minutes / 60.0, 1)

    # 6. Faculty Feedback & Mentorship Targets
    recent_feedback = profile.feedback_received.order_by(FacultyFeedback.created_at.desc()).limit(3).all()
    pending_targets = profile.mentorship_targets.filter_by(status='Pending').order_by(MentorshipTarget.deadline.asc()).limit(3).all()

    # 7. Recent activities
    recent_activities = profile.activity_logs.order_by(StudentActivityLog.created_at.desc()).limit(7).all()

    return render_template(
        'student/dashboard.html',
        profile=profile,
        total_skills=total_skills,
        learning_skills=learning_skills,
        mastered_skills=mastered_skills,
        avg_proficiency=avg_proficiency,
        study_plan_completion=study_plan_completion,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        upcoming_tasks=upcoming_tasks,
        active_projects=active_projects,
        completed_projects=completed_projects,
        total_quizzes=total_quizzes,
        passed_quizzes=passed_quizzes,
        avg_score=avg_score,
        weekly_hours=weekly_hours,
        heatmap=heatmap,
        recent_feedback=recent_feedback,
        pending_targets=pending_targets,
        recent_activities=recent_activities,
        current_year=year
    )

@student_bp.route('/log-session', methods=['POST'])
def log_session():
    """Allows students to log a dedicated self-study or coding practice session."""
    profile = current_user.student_profile
    topic = request.form.get('topic', 'Self-Directed Learning')
    duration = int(request.form.get('duration', 45))
    activity_type = request.form.get('activity_type', 'learning_session')

    log_activity(
        student_id=profile.id,
        activity_type=activity_type,
        activity_title=f"Study Session: {topic}",
        duration_minutes=duration
    )
    flash(f'Logged {duration} mins for "{topic}"! Streak and heatmap updated.', 'success')
    return redirect(url_for('student.dashboard'))
