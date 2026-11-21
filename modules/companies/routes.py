from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import date
from extensions import db
from models.company import Company, JobRole, JobRoleSkill

companies_bp = Blueprint('companies', __name__, url_prefix='/companies')

@companies_bp.route('/')
@login_required
def index():
    search = request.args.get('q', '').strip()
    category_filter = request.args.get('category', 'all')
    tier_filter = request.args.get('tier', 'all')
    role_filter = request.args.get('role', 'all')

    query = Company.query

    if category_filter != 'all':
        query = query.filter_by(industry=category_filter)

    if tier_filter != 'all':
        query = query.filter_by(tier=tier_filter)

    if search:
        query = query.filter(Company.name.ilike(f"%{search}%") | Company.description.ilike(f"%{search}%"))

    companies = query.order_by(Company.name).all()

    # If role filter applied
    if role_filter != 'all':
        companies = [c for c in companies if any(role_filter.lower() in r.title.lower() for r in c.job_roles)]

    # Collect distinct industries
    industries = [
        "Global Tech MNCs",
        "Product & Fintech",
        "Sales, Consulting & Management",
        "Pharmaceutical & Healthcare"
    ]

    return render_template(
        'companies/index.html',
        companies=companies,
        search=search,
        category_filter=category_filter,
        tier_filter=tier_filter,
        role_filter=role_filter,
        industries=industries
    )


@companies_bp.route('/add-custom', methods=['POST'])
@login_required
def add_custom():
    """Allows students/faculty/admin to add or suggest an unlisted custom company."""
    name = request.form.get('company_name', '').strip()
    industry = request.form.get('industry', 'Global Tech MNCs').strip()
    website = request.form.get('website', '').strip()
    description = request.form.get('description', '').strip()
    role_title = request.form.get('role_title', 'Campus Associate').strip()
    ctc = request.form.get('ctc_range', 'Competitive LPA').strip()

    if not name:
        flash('Company name is required.', 'danger')
        return redirect(url_for('companies.index'))

    existing = Company.query.filter_by(name=name).first()
    if existing:
        flash(f'Company "{name}" already exists in the catalog!', 'info')
        return redirect(url_for('companies.index', q=name))

    new_comp = Company(
        name=name,
        industry=industry,
        tier="Custom / Student Added",
        website=website or "https://" + name.lower().replace(" ", "") + ".com",
        careers_url=website or "https://" + name.lower().replace(" ", "") + ".com/careers",
        description=description or f"Custom target company {name} added for career readiness and placement tracking.",
        is_verified=True,
        last_verified_date=date.today()
    )
    db.session.add(new_comp)
    db.session.flush()

    role = JobRole(
        company_id=new_comp.id,
        title=role_title,
        description=f"Recruitment track for {name}.",
        ctc_range=ctc,
        min_cgpa=6.0
    )
    db.session.add(role)
    db.session.commit()

    flash(f'Company "{name}" has been successfully added to your catalog and is now available for tracking!', 'success')
    return redirect(url_for('companies.index', q=name))


@companies_bp.route('/<int:company_id>')
@login_required
def detail(company_id):
    company = Company.query.get_or_404(company_id)
    return render_template('companies/detail.html', company=company)
