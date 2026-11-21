from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from extensions import db
from models.study_plan import StudyPlan, StudyTask
from models.company import Company, JobRole
from services.ai_service import AIService
from services.activity_service import log_activity

study_planner_bp = Blueprint('study_planner', __name__, url_prefix='/study-plans')

@study_planner_bp.route('/')
@login_required
def index():
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile

    plans = profile.study_plans.order_by(StudyPlan.created_at.desc()).all()
    selected_plan_id = request.args.get('plan_id', type=int)

    selected_plan = None
    if selected_plan_id:
        selected_plan = StudyPlan.query.filter_by(id=selected_plan_id, student_id=profile.id).first()

    if not selected_plan and plans:
        selected_plan = plans[0]

    tasks = []
    if selected_plan:
        status_filter = request.args.get('status', 'all')
        query = selected_plan.tasks
        if status_filter == 'pending':
            query = query.filter_by(is_completed=False)
        elif status_filter == 'completed':
            query = query.filter_by(is_completed=True)
        tasks = query.order_by(StudyTask.scheduled_date.asc(), StudyTask.priority.desc()).all()

    companies = Company.query.order_by(Company.name).all()

    return render_template(
        'study_planner/index.html',
        plans=plans,
        selected_plan=selected_plan,
        tasks=tasks,
        companies=companies
    )


@study_planner_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile

    title = request.form.get('title', '').strip() or 'AI Placement Sprint'
    target_company = request.form.get('target_company', 'TCS')
    target_role = request.form.get('target_role', 'Software Engineer')
    weekly_hours = int(request.form.get('weekly_hours', 14))

    # Look up required skills for this target
    job_role = JobRole.query.filter(JobRole.title.ilike(f"%{target_role}%")).first()
    required_skills = job_role.required_skills if job_role else []

    # Run gap analysis to extract missing & weak topics
    gap = AIService.analyze_skill_gap(profile.skills.all(), required_skills, target_company, target_role)
    missing = [m['name'] for m in gap['missing_skills']]
    weak = [w['name'] for w in gap['weak_skills']]

    # Generate tasks using AI / Rule engine
    tasks_data, engine_source = AIService.generate_study_plan(
        student_profile=profile,
        target_company=target_company,
        target_role=target_role,
        missing_skills=missing,
        weak_skills=weak,
        weekly_hours=weekly_hours
    )

    # Save StudyPlan
    new_plan = StudyPlan(
        student_id=profile.id,
        title=title,
        target_company=target_company,
        target_role=target_role,
        weekly_hours=weekly_hours,
        start_date=date.today(),
        target_date=date.today() + timedelta(days=30),
        ai_generated=True,
        status='Active'
    )
    db.session.add(new_plan)
    db.session.flush()

    for item in tasks_data:
        task = StudyTask(
            plan_id=new_plan.id,
            student_id=profile.id,
            title=item.get('title', 'Study Task'),
            skill_name=item.get('skill_name', 'General'),
            topic=item.get('topic', 'Core Topic'),
            description=item.get('description', ''),
            duration_minutes=int(item.get('duration_minutes', 45)),
            priority=item.get('priority', 'High'),
            scheduled_date=date.fromisoformat(item['scheduled_date']) if 'scheduled_date' in item and isinstance(item['scheduled_date'], str) else date.today(),
            deadline=date.fromisoformat(item['deadline']) if 'deadline' in item and isinstance(item['deadline'], str) else date.today() + timedelta(days=3),
            resources=item.get('resources', '')
        )
        db.session.add(task)

    db.session.commit()
    flash(f'Study Plan "{title}" successfully created via {engine_source} with {len(tasks_data)} tasks!', 'success')
    return redirect(url_for('study_planner.index', plan_id=new_plan.id))


@study_planner_bp.route('/toggle-task/<int:task_id>', methods=['POST'])
@login_required
def toggle_task(task_id):
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile
    task = StudyTask.query.filter_by(id=task_id, student_id=profile.id).first_or_404()

    task.is_completed = not task.is_completed
    if task.is_completed:
        task.completed_at = datetime.utcnow()
        # Log qualifying activity into student_activity_logs (Updates heatmap & streak)
        log_activity(
            student_id=profile.id,
            activity_type='study_task',
            activity_title=f"Completed: {task.title}",
            duration_minutes=task.duration_minutes,
            related_record_id=task.id
        )
        flash(f'Awesome! Completed "{task.title}". Heatmap and streak updated!', 'success')
    else:
        task.completed_at = None
        flash(f'Task marked as pending.', 'info')

    db.session.commit()
    return redirect(url_for('study_planner.index', plan_id=task.plan_id))


@study_planner_bp.route('/add-task', methods=['POST'])
@login_required
def add_task():
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile

    plan_id = request.form.get('plan_id', type=int)
    plan = StudyPlan.query.filter_by(id=plan_id, student_id=profile.id).first_or_404()

    title = request.form.get('title', '').strip()
    topic = request.form.get('topic', '').strip()
    skill_name = request.form.get('skill_name', 'General')
    duration = int(request.form.get('duration_minutes', 45))
    priority = request.form.get('priority', 'Medium')
    scheduled_str = request.form.get('scheduled_date')
    sched_date = date.fromisoformat(scheduled_str) if scheduled_str else date.today()

    task = StudyTask(
        plan_id=plan.id,
        student_id=profile.id,
        title=title,
        topic=topic or title,
        skill_name=skill_name,
        duration_minutes=duration,
        priority=priority,
        scheduled_date=sched_date,
        deadline=sched_date + timedelta(days=2),
        is_completed=False
    )
    db.session.add(task)
    db.session.commit()
    flash(f'Personal task "{title}" added to your study plan.', 'success')
    return redirect(url_for('study_planner.index', plan_id=plan.id))
