from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from models.company import Company, JobRole
from services.ai_service import AIService

skill_gap_bp = Blueprint('skill_gap', __name__, url_prefix='/skill-gap')

@skill_gap_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile
    companies = Company.query.order_by(Company.name).all()

    company_id = request.args.get('company_id', type=int) or request.form.get('company_id', type=int)
    role_id = request.args.get('role_id', type=int) or request.form.get('role_id', type=int)

    selected_company = None
    selected_role = None
    gap_result = None

    if company_id:
        selected_company = Company.query.get(company_id)
        if selected_company and not role_id and selected_company.job_roles:
            selected_role = selected_company.job_roles[0]
            role_id = selected_role.id

    if role_id:
        selected_role = JobRole.query.get(role_id)
        if selected_role:
            selected_company = selected_role.company

    if selected_company and selected_role:
        student_skills = profile.skills.all()
        required_skills = selected_role.required_skills
        gap_result = AIService.analyze_skill_gap(
            student_skills=student_skills,
            required_skills=required_skills,
            target_company=selected_company.name,
            target_role=selected_role.title
        )

    return render_template(
        'skill_gap/index.html',
        companies=companies,
        selected_company=selected_company,
        selected_role=selected_role,
        gap_result=gap_result,
        student_profile=profile
    )
