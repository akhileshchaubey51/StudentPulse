from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime
import json
from extensions import db
from models.user import User, StudentProfile, FacultyProfile
from models.academic import Department, Course, Semester, Batch, Section, StudentBatchAssignment, FacultyBatchAssignment, FacultyStudentAssignment
from models.company import Company, JobRole, JobRoleSkill
from models.skill import Skill
from models.assessment import Question, Assessment, AssessmentQuestion
from models.activity import StudentStreak

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
@login_required
def check_admin_role():
    if not current_user.is_admin():
        abort(403)

@admin_bp.route('/dashboard')
def dashboard():
    total_students = StudentProfile.query.count()
    total_faculty = FacultyProfile.query.count()
    total_companies = Company.query.count()
    total_batches = Batch.query.count()

    # Active streaks across the institution
    active_streaks = StudentStreak.query.filter(StudentStreak.current_streak > 0).count()
    longest_streak_record = db.session.query(db.func.max(StudentStreak.longest_streak)).scalar() or 0

    departments = Department.query.all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(8).all()

    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_faculty=total_faculty,
        total_companies=total_companies,
        total_batches=total_batches,
        active_streaks=active_streaks,
        longest_streak_record=longest_streak_record,
        departments=departments,
        recent_users=recent_users
    )


@admin_bp.route('/reset-demo-data', methods=['POST'])
def reset_demo_data():
    from models.activity import StudentActivityLog, StudentStreak
    from models.assessment import AssessmentAttempt, AssessmentAnswer
    from models.interview import MockInterview, InterviewResponse
    from models.faculty import FacultyFeedback, MentorshipTarget

    StudentActivityLog.query.delete()
    for s in StudentStreak.query.all():
        s.current_streak = 0
        s.longest_streak = 0
        s.total_active_days = 0
        s.last_active_date = None
    AssessmentAnswer.query.delete()
    AssessmentAttempt.query.delete()
    InterviewResponse.query.delete()
    MockInterview.query.delete()
    FacultyFeedback.query.delete()
    MentorshipTarget.query.delete()

    db.session.commit()
    flash('Demo activity records and simulated mock history wiped successfully. System reset to clean state.', 'info')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users')
def users():
    role_filter = request.args.get('role', 'all')
    search = request.args.get('q', '').strip()

    query = User.query
    if role_filter != 'all':
        query = query.filter_by(role=role_filter)
    if search:
        query = query.filter(User.email.ilike(f"%{search}%") | User.first_name.ilike(f"%{search}%") | User.last_name.ilike(f"%{search}%"))

    users_list = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list, role_filter=role_filter, search=search)


@admin_bp.route('/create-user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        role = request.form.get('role', 'student')

        if User.query.filter_by(email=email).first():
            flash('A user with this email already exists.', 'danger')
            return redirect(url_for('admin.users'))

        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if role == 'student':
            enrollment = request.form.get('enrollment_number', f"STU{user.id:04d}")
            dept = request.form.get('department', 'Computer Science & Engineering')
            stud = StudentProfile(
                user_id=user.id,
                enrollment_number=enrollment,
                department=dept,
                graduation_year=int(request.form.get('graduation_year', 2026))
            )
            db.session.add(stud)
            db.session.flush()
            streak = StudentStreak(student_id=stud.id, current_streak=0, longest_streak=0, total_active_days=0)
            db.session.add(streak)

        elif role == 'faculty':
            faculty_id = request.form.get('faculty_id', f"FAC{user.id:03d}")
            dept = request.form.get('department', 'Computer Science & Engineering')
            designation = request.form.get('designation', 'Assistant Professor')
            fac = FacultyProfile(
                user_id=user.id,
                faculty_id=faculty_id,
                department=dept,
                designation=designation
            )
            db.session.add(fac)

        db.session.commit()
        flash(f'Account created successfully for {user.full_name} ({role})!', 'success')
        return redirect(url_for('admin.users'))

    departments = Department.query.all()
    return render_template('admin/create_user.html', departments=departments)


@admin_bp.route('/toggle-user/<int:user_id>', methods=['POST'])
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own administrative account.', 'danger')
        return redirect(url_for('admin.users'))

    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.email} has been {status}.', 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/academic')
def academic():
    depts = Department.query.all()
    batches = Batch.query.all()
    faculty_profiles = FacultyProfile.query.all()
    return render_template('admin/academic.html', departments=depts, batches=batches, faculty_profiles=faculty_profiles)


@admin_bp.route('/create-department', methods=['POST'])
def create_department():
    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip().upper()
    desc = request.form.get('description', '').strip()

    if Department.query.filter_by(code=code).first():
        flash('Department with this code already exists.', 'warning')
        return redirect(url_for('admin.academic'))

    dept = Department(name=name, code=code, description=desc)
    db.session.add(dept)
    db.session.commit()
    flash(f'Department "{name}" created.', 'success')
    return redirect(url_for('admin.academic'))


@admin_bp.route('/assign-faculty-batch', methods=['POST'])
def assign_faculty_batch():
    faculty_id = request.form.get('faculty_id', type=int)
    batch_id = request.form.get('batch_id', type=int)

    existing = FacultyBatchAssignment.query.filter_by(faculty_id=faculty_id, batch_id=batch_id).first()
    if not existing:
        assignment = FacultyBatchAssignment(faculty_id=faculty_id, batch_id=batch_id)
        db.session.add(assignment)
        db.session.commit()
        flash('Faculty member successfully assigned to batch.', 'success')
    else:
        flash('This faculty assignment already exists.', 'info')
    return redirect(url_for('admin.academic'))


@admin_bp.route('/companies', methods=['GET', 'POST'])
def companies():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        website = request.form.get('website', '').strip()
        careers_url = request.form.get('careers_url', '').strip()
        source_url = request.form.get('source_url', '').strip()
        description = request.form.get('description', '').strip()
        tier = request.form.get('tier', 'Tier 1')

        comp = Company(
            name=name,
            website=website,
            careers_url=careers_url,
            source_url=source_url,
            description=description,
            tier=tier,
            is_verified=True,
            last_verified_date=datetime.utcnow()
        )
        db.session.add(comp)
        db.session.commit()
        flash(f'Company "{name}" registered.', 'success')
        return redirect(url_for('admin.companies'))

    comps = Company.query.order_by(Company.name).all()
    skills = Skill.query.order_by(Skill.name).all()
    return render_template('admin/companies.html', companies=comps, skills=skills)


@admin_bp.route('/add-job-role', methods=['POST'])
def add_job_role():
    company_id = request.form.get('company_id', type=int)
    title = request.form.get('title', '').strip()
    ctc = request.form.get('ctc_range', '4.5 - 9.0 LPA')
    min_cgpa = float(request.form.get('min_cgpa', 6.5))
    selection_process = request.form.get('selection_process', 'Online Test -> Technical -> HR')

    role = JobRole(
        company_id=company_id,
        title=title,
        ctc_range=ctc,
        min_cgpa=min_cgpa,
        selection_process=selection_process
    )
    db.session.add(role)
    db.session.flush()

    # Link skills
    skill_ids = request.form.getlist('skill_ids')
    for s_id in skill_ids:
        jrs = JobRoleSkill(
            job_role_id=role.id,
            skill_id=int(s_id),
            is_required=True,
            minimum_proficiency='Intermediate'
        )
        db.session.add(jrs)

    db.session.commit()
    flash(f'Job role "{title}" added with required skills.', 'success')
    return redirect(url_for('admin.companies'))


@admin_bp.route('/questions', methods=['GET', 'POST'])
def questions():
    if request.method == 'POST':
        cat = request.form.get('category', 'DSA')
        sub_topic = request.form.get('sub_topic', 'General')
        difficulty = request.form.get('difficulty', 'Medium')
        q_text = request.form.get('question_text', '').strip()
        options = [
            request.form.get('opt0', '').strip(),
            request.form.get('opt1', '').strip(),
            request.form.get('opt2', '').strip(),
            request.form.get('opt3', '').strip()
        ]
        correct = int(request.form.get('correct_option', 0))
        explanation = request.form.get('explanation', '').strip()

        q = Question(
            category=cat,
            sub_topic=sub_topic,
            difficulty=difficulty,
            question_text=q_text,
            options_json=json.dumps(options),
            correct_option=correct,
            explanation=explanation
        )
        db.session.add(q)
        db.session.commit()
        flash('Question successfully added to question bank!', 'success')
        return redirect(url_for('admin.questions'))

    q_list = Question.query.order_by(Question.id.desc()).all()
    return render_template('admin/questions.html', questions=q_list)
