from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime
from extensions import db
from models.skill import Skill, StudentSkill
from services.activity_service import log_activity

skills_bp = Blueprint('skills', __name__, url_prefix='/skills')

@skills_bp.route('/')
@login_required
def index():
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile

    category_filter = request.args.get('category', 'all')
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('q', '').strip().lower()

    query = StudentSkill.query.filter_by(student_id=profile.id).join(Skill)

    if category_filter != 'all':
        query = query.filter(Skill.category == category_filter)
    if status_filter != 'all':
        query = query.filter(StudentSkill.learning_status == status_filter)
    if search_query:
        query = query.filter(Skill.name.ilike(f"%{search_query}%"))

    student_skills = query.order_by(StudentSkill.last_updated.desc()).all()

    # Pre-existing global skills available to add
    existing_skill_ids = [s.skill_id for s in profile.skills.all()]
    available_catalog_skills = Skill.query.filter(~Skill.id.in_(existing_skill_ids)).order_by(Skill.name).all() if existing_skill_ids else Skill.query.order_by(Skill.name).all()

    # Metrics
    all_stud_skills = profile.skills.all()
    tech_count = sum(1 for s in all_stud_skills if s.skill.category == 'Technical')
    non_tech_count = sum(1 for s in all_stud_skills if s.skill.category == 'Non-Technical')
    mastered_count = sum(1 for s in all_stud_skills if s.proficiency in ('Advanced', 'Expert'))

    return render_template(
        'skills/index.html',
        student_skills=student_skills,
        available_catalog_skills=available_catalog_skills,
        tech_count=tech_count,
        non_tech_count=non_tech_count,
        mastered_count=mastered_count,
        category_filter=category_filter,
        status_filter=status_filter,
        search_query=search_query
    )


@skills_bp.route('/add', methods=['POST'])
@login_required
def add():
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile

    skill_id = request.form.get('skill_id')
    custom_name = request.form.get('custom_name', '').strip()
    category = request.form.get('category', 'Technical')
    proficiency = request.form.get('proficiency', 'Beginner')
    learning_status = request.form.get('learning_status', 'Learning')
    self_score = int(request.form.get('self_score', 50))
    evidence_url = request.form.get('evidence_url', '').strip()
    notes = request.form.get('notes', '').strip()

    if skill_id:
        target_skill = Skill.query.get(int(skill_id))
    elif custom_name:
        target_skill = Skill.query.filter_by(name=custom_name).first()
        if not target_skill:
            target_skill = Skill(name=custom_name, category=category, sub_category='Custom')
            db.session.add(target_skill)
            db.session.flush()
    else:
        flash('Please select or specify a skill name.', 'danger')
        return redirect(url_for('skills.index'))

    existing = StudentSkill.query.filter_by(student_id=profile.id, skill_id=target_skill.id).first()
    if existing:
        flash('This skill is already in your profile. You can edit its details below.', 'warning')
        return redirect(url_for('skills.index'))

    new_stud_skill = StudentSkill(
        student_id=profile.id,
        skill_id=target_skill.id,
        proficiency=proficiency,
        learning_status=learning_status,
        self_score=self_score,
        evidence_url=evidence_url,
        notes=notes,
        last_updated=datetime.utcnow()
    )
    db.session.add(new_stud_skill)
    db.session.commit()

    log_activity(
        student_id=profile.id,
        activity_type='skill_assessment',
        activity_title=f"Added Skill: {target_skill.name} ({proficiency})",
        duration_minutes=20,
        related_record_id=new_stud_skill.id
    )

    flash(f'Skill "{target_skill.name}" added successfully to your profile!', 'success')
    return redirect(url_for('skills.index'))


@skills_bp.route('/update/<int:skill_id>', methods=['POST'])
@login_required
def update(skill_id):
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile
    stud_skill = StudentSkill.query.filter_by(student_id=profile.id, id=skill_id).first_or_404()

    old_prof = stud_skill.proficiency
    new_prof = request.form.get('proficiency', stud_skill.proficiency)
    stud_skill.proficiency = new_prof
    stud_skill.learning_status = request.form.get('learning_status', stud_skill.learning_status)
    stud_skill.self_score = int(request.form.get('self_score', stud_skill.self_score))
    stud_skill.evidence_url = request.form.get('evidence_url', stud_skill.evidence_url)
    stud_skill.notes = request.form.get('notes', stud_skill.notes)
    stud_skill.last_updated = datetime.utcnow()

    db.session.commit()

    if old_prof != new_prof:
        log_activity(
            student_id=profile.id,
            activity_type='skill_assessment',
            activity_title=f"Leveled Up {stud_skill.skill.name}: {old_prof} -> {new_prof}",
            duration_minutes=30,
            related_record_id=stud_skill.id
        )

    flash(f'Skill "{stud_skill.skill.name}" updated successfully.', 'success')
    return redirect(url_for('skills.index'))


@skills_bp.route('/delete/<int:skill_id>', methods=['POST'])
@login_required
def delete(skill_id):
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile
    stud_skill = StudentSkill.query.filter_by(student_id=profile.id, id=skill_id).first_or_404()
    name = stud_skill.skill.name
    db.session.delete(stud_skill)
    db.session.commit()
    flash(f'Skill "{name}" removed from your profile.', 'info')
    return redirect(url_for('skills.index'))
