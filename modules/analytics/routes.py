from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from datetime import date, timedelta
from extensions import db
from models.activity import StudentActivityLog, StudentStreak
from models.assessment import AssessmentAttempt
from models.study_plan import StudyTask

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/')
@login_required
def index():
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile

    # 1. Past 7 days hours trend
    today = date.today()
    days_labels = []
    days_hours = []

    for i in range(6, -1, -1):
        target_d = today - timedelta(days=i)
        days_labels.append(target_d.strftime('%a (%d %b)'))
        logs = StudentActivityLog.query.filter(
            StudentActivityLog.student_id == profile.id,
            StudentActivityLog.activity_date == target_d,
            StudentActivityLog.status == 'completed'
        ).all()
        mins = sum(l.duration_minutes for l in logs)
        days_hours.append(round(mins / 60.0, 1))

    # 2. Activity category distribution
    all_logs = StudentActivityLog.query.filter_by(student_id=profile.id, status='completed').all()
    categories_count = {}
    for l in all_logs:
        name = l.activity_type.replace('_', ' ').title()
        categories_count[name] = categories_count.get(name, 0) + 1

    # 3. Assessment performance trends
    attempts = AssessmentAttempt.query.filter_by(student_id=profile.id).order_by(AssessmentAttempt.completed_at.asc()).all()
    attempt_labels = [a.assessment.title[:15] + '...' for a in attempts]
    attempt_scores = [a.score for a in attempts]

    # 4. Overall metrics
    streak = StudentStreak.query.filter_by(student_id=profile.id).first()
    total_active_days = streak.total_active_days if streak else 0
    total_hours = round(sum(l.duration_minutes for l in all_logs) / 60.0, 1)

    return render_template(
        'analytics/index.html',
        profile=profile,
        days_labels=days_labels,
        days_hours=days_hours,
        cat_labels=list(categories_count.keys()),
        cat_data=list(categories_count.values()),
        attempt_labels=attempt_labels,
        attempt_scores=attempt_scores,
        total_active_days=total_active_days,
        total_hours=total_hours,
        current_streak=streak.current_streak if streak else 0,
        longest_streak=streak.longest_streak if streak else 0
    )
