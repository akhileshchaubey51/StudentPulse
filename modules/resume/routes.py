from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime
import json
from extensions import db
from models.resume import Resume

resume_bp = Blueprint('resume', __name__, url_prefix='/resume')

@resume_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile

    resume = Resume.query.filter_by(student_id=profile.id).first()
    if not resume:
        resume = Resume(
            student_id=profile.id,
            template_name='Classic Tech',
            summary=profile.career_objective,
            certifications_json=json.dumps(["Certified Python Associate", "Oracle Certified Foundations Associate: Database"]),
            achievements_json=json.dumps(["Dean's Honor Roll - 5th Semester", "Finalist - Smart Campus Hackathon 2025"]),
            experience_json=json.dumps([{"role": "Software Engineering Intern", "company": "Tech Innovators Lab", "duration": "June 2025 - August 2025", "details": "Engineered REST APIs using Flask and optimized SQL queries."}])
        )
        db.session.add(resume)
        db.session.commit()

    if request.method == 'POST':
        resume.summary = request.form.get('summary', '').strip()
        resume.template_name = request.form.get('template_name', 'Classic Tech')

        certs_raw = request.form.get('certifications', '').strip()
        certs_list = [c.strip() for c in certs_raw.split('\n') if c.strip()]
        resume.certifications_json = json.dumps(certs_list)

        achieve_raw = request.form.get('achievements', '').strip()
        achieve_list = [a.strip() for a in achieve_raw.split('\n') if a.strip()]
        resume.achievements_json = json.dumps(achieve_list)

        resume.last_updated = datetime.utcnow()
        db.session.commit()
        flash('Resume details updated successfully!', 'success')
        return redirect(url_for('resume.index'))

    # Completeness check
    skills_count = profile.skills.count()
    projects_count = profile.projects.count()
    completeness = 40
    if skills_count >= 3: completeness += 20
    if projects_count >= 1: completeness += 20
    if resume.get_certifications(): completeness += 10
    if resume.get_achievements(): completeness += 10

    return render_template(
        'resume/index.html',
        profile=profile,
        resume=resume,
        skills=profile.skills.all(),
        projects=profile.projects.all(),
        completeness=completeness
    )


@resume_bp.route('/preview')
@login_required
def preview():
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile
    resume = Resume.query.filter_by(student_id=profile.id).first_or_404()
    return render_template(
        'resume/preview.html',
        profile=profile,
        resume=resume,
        skills=profile.skills.all(),
        projects=profile.projects.all()
    )
