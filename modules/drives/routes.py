from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime, date
from extensions import db
from models.campus_drive import CampusDrive, DriveApplication
from models.company import Company
from services.notification_service import send_notification
from models.user import StudentProfile, User

drives_bp = Blueprint('drives', __name__, url_prefix='/drives')

@drives_bp.route('/')
@login_required
def index():
    course_filter = request.args.get('course', 'all')
    status_filter = request.args.get('status', 'all')
    search = request.args.get('q', '').strip()

    query = CampusDrive.query

    if status_filter != 'all':
        query = query.filter_by(status=status_filter)

    drives = query.order_by(CampusDrive.last_date_to_apply.asc()).all()

    # Filter in python for comma-separated courses
    if course_filter != 'all':
        drives = [d for d in drives if course_filter.lower() in d.eligible_courses.lower()]

    if search:
        drives = [d for d in drives if search.lower() in d.title.lower() or search.lower() in d.company.name.lower()]

    user_applications = {}
    if current_user.is_student() and current_user.student_profile:
        for app in current_user.student_profile.drive_applications:
            user_applications[app.drive_id] = app

    companies = Company.query.order_by(Company.name).all()

    return render_template(
        'drives/index.html',
        drives=drives,
        user_applications=user_applications,
        companies=companies,
        course_filter=course_filter,
        status_filter=status_filter,
        search=search,
        today=date.today()
    )


@drives_bp.route('/post', methods=['POST'])
@login_required
def post_drive():
    if not (current_user.is_admin() or current_user.is_faculty()):
        abort(403)

    company_id = int(request.form.get('company_id'))
    title = request.form.get('title', '').strip()
    courses = request.form.getlist('courses')
    eligible_courses = ", ".join(courses) if courses else request.form.get('custom_courses', 'All Courses')
    min_cgpa = float(request.form.get('min_cgpa', 6.0))
    package_ctc = request.form.get('package_ctc', '4.5 - 8.0 LPA')
    drive_date_str = request.form.get('drive_date')
    last_date_str = request.form.get('last_date_to_apply')
    location = request.form.get('job_location', 'Campus / Hybrid')
    description = request.form.get('description', '').strip()
    selection_process = request.form.get('selection_process', 'Online Test -> Technical -> HR')

    drive = CampusDrive(
        company_id=company_id,
        title=title,
        eligible_courses=eligible_courses,
        min_cgpa=min_cgpa,
        package_ctc=package_ctc,
        drive_date=date.fromisoformat(drive_date_str) if drive_date_str else date.today(),
        last_date_to_apply=date.fromisoformat(last_date_str) if last_date_str else date.today(),
        job_location=location,
        description=description,
        selection_process=selection_process,
        status='Active'
    )
    db.session.add(drive)
    db.session.commit()

    # Notify all students
    all_students = User.query.filter_by(role='student', is_active=True).all()
    comp = Company.query.get(company_id)
    comp_name = comp.name if comp else "Company"
    for st in all_students:
        send_notification(
            user_id=st.id,
            title=f"New Campus Hiring Drive: {comp_name}",
            message=f"{title} is now open for {eligible_courses}. Package: {package_ctc}. Apply before {drive.last_date_to_apply}!",
            category='success',
            link=url_for('drives.index')
        )

    flash(f'Campus Drive "{title}" published successfully! All eligible students notified.', 'success')
    return redirect(url_for('drives.index'))


@drives_bp.route('/apply/<int:drive_id>', methods=['POST'])
@login_required
def apply(drive_id):
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile
    drive = CampusDrive.query.get_or_404(drive_id)

    if drive.is_expired():
        flash('The application deadline for this campus drive has passed.', 'warning')
        return redirect(url_for('drives.index'))

    existing = DriveApplication.query.filter_by(drive_id=drive.id, student_id=profile.id).first()
    if existing:
        flash('You have already submitted an application for this drive.', 'info')
        return redirect(url_for('drives.index'))

    application = DriveApplication(
        drive_id=drive.id,
        student_id=profile.id,
        status='Applied'
    )
    db.session.add(application)
    db.session.commit()

    flash(f'Application submitted for "{drive.company.name} - {drive.title}"! Placement cell will review your profile.', 'success')
    return redirect(url_for('drives.index'))


@drives_bp.route('/applicants/<int:drive_id>')
@login_required
def applicants(drive_id):
    if not (current_user.is_admin() or current_user.is_faculty()):
        abort(403)
    drive = CampusDrive.query.get_or_404(drive_id)
    return render_template('drives/applicants.html', drive=drive)


@drives_bp.route('/update-status/<int:app_id>', methods=['POST'])
@login_required
def update_status(app_id):
    if not (current_user.is_admin() or current_user.is_faculty()):
        abort(403)
    application = DriveApplication.query.get_or_404(app_id)
    new_status = request.form.get('status', 'Applied')
    application.status = new_status
    db.session.commit()

    # Notify student
    send_notification(
        user_id=application.student.user_id,
        title=f"Placement Drive Status Update: {application.drive.company.name}",
        message=f"Your application status for {application.drive.title} was updated to: {new_status}.",
        category='info' if new_status != 'Selected' else 'success',
        link=url_for('drives.index')
    )

    flash(f"Updated status for {application.student.user.full_name} to {new_status}.", 'success')
    return redirect(url_for('drives.applicants', drive_id=application.drive_id))
