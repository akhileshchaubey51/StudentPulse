from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime
from extensions import db
from models.assessment import Assessment, Question, AssessmentAttempt, AssessmentAnswer
from services.activity_service import log_activity

coding_bp = Blueprint('coding', __name__, url_prefix='/coding')

@coding_bp.route('/')
@login_required
def index():
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile

    category = request.args.get('category', 'all')
    query = Assessment.query.filter_by(is_active=True)

    if category != 'all':
        query = query.filter_by(category=category)

    assessments = query.all()
    past_attempts = profile.assessment_attempts.order_by(AssessmentAttempt.completed_at.desc()).limit(10).all()

    # Practice stats
    total_attempts = len(profile.assessment_attempts.all())
    passed_attempts = sum(1 for a in profile.assessment_attempts if a.passed)
    accuracy = int((passed_attempts / total_attempts * 100)) if total_attempts > 0 else 0
    total_bank_questions = Question.query.count()

    return render_template(
        'coding/index.html',
        assessments=assessments,
        past_attempts=past_attempts,
        category=category,
        total_attempts=total_attempts,
        accuracy=accuracy,
        total_bank_questions=total_bank_questions
    )


@coding_bp.route('/practice')
@login_required
def practice():
    """Interactive practice questions portal with 25+ questions across tech, math, aptitude & domain."""
    category = request.args.get('category', 'all')
    difficulty = request.args.get('difficulty', 'all')
    search = request.args.get('q', '').strip()

    query = Question.query
    if category != 'all':
        query = query.filter_by(category=category)
    if difficulty != 'all':
        query = query.filter_by(difficulty=difficulty)
    if search:
        query = query.filter(Question.question_text.ilike(f"%{search}%") | Question.sub_topic.ilike(f"%{search}%"))

    questions = query.all()
    categories = [c[0] for c in db.session.query(Question.category).distinct().all()]

    return render_template(
        'coding/practice.html',
        questions=questions,
        category=category,
        difficulty=difficulty,
        search=search,
        categories=categories
    )


@coding_bp.route('/generate-ai-questions', methods=['POST'])
@login_required
def generate_ai_questions():
    """Generates 5 brand new dynamic AI practice questions that never repeat."""
    if not current_user.is_student():
        abort(403)
    category = request.form.get('category', 'all')
    difficulty = request.form.get('difficulty', 'all')
    count = int(request.form.get('count', 5))

    from services.ai_service import AIService
    new_q = AIService.generate_dynamic_ai_questions(category=category, difficulty=difficulty, count=count)
    flash(f'✨ Generated {len(new_q)} fresh AI practice questions! Each question was synthesized dynamically and will never repeat.', 'success')
    return redirect(url_for('coding.practice', category=category if category != 'all' else None))


@coding_bp.route('/take/<int:assessment_id>')
@login_required
def take(assessment_id):
    if not current_user.is_student():
        abort(403)
    assessment = Assessment.query.get_or_404(assessment_id)
    questions = [aq.question for aq in assessment.questions]
    return render_template('coding/take.html', assessment=assessment, questions=questions)


@coding_bp.route('/submit/<int:assessment_id>', methods=['POST'])
@login_required
def submit(assessment_id):
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile
    assessment = Assessment.query.get_or_404(assessment_id)

    questions = [aq.question for aq in assessment.questions]
    total_q = len(questions)
    correct_count = 0

    attempt = AssessmentAttempt(
        assessment_id=assessment.id,
        student_id=profile.id,
        total_questions=total_q,
        completed_at=datetime.utcnow()
    )
    db.session.add(attempt)
    db.session.flush()

    for q in questions:
        field_name = f"question_{q.id}"
        selected = request.form.get(field_name)
        selected_idx = int(selected) if selected is not None and selected.isdigit() else None
        is_corr = (selected_idx == q.correct_option)
        if is_corr:
            correct_count += 1

        ans = AssessmentAnswer(
            attempt_id=attempt.id,
            question_id=q.id,
            selected_option=selected_idx,
            is_correct=is_corr
        )
        db.session.add(ans)

    score_pct = int((correct_count / total_q) * 100) if total_q > 0 else 0
    attempt.score = score_pct
    attempt.correct_answers = correct_count
    attempt.passed = (score_pct >= assessment.passing_score)

    db.session.commit()

    # Log activity for heatmap & streak
    log_activity(
        student_id=profile.id,
        activity_type='coding_quiz',
        activity_title=f"Assessment: {assessment.title} ({score_pct}%)",
        duration_minutes=assessment.duration_minutes,
        related_record_id=attempt.id
    )

    if attempt.passed:
        flash(f'Congratulations! You passed with {score_pct}% ({correct_count}/{total_q}). Heatmap & streak updated!', 'success')
    else:
        flash(f'Assessment completed: {score_pct}%. Passing is {assessment.passing_score}%. Review questions below to strengthen concepts.', 'warning')

    return redirect(url_for('coding.result', attempt_id=attempt.id))


@coding_bp.route('/result/<int:attempt_id>')
@login_required
def result(attempt_id):
    if not current_user.is_student():
        abort(403)
    profile = current_user.student_profile
    attempt = AssessmentAttempt.query.filter_by(id=attempt_id, student_id=profile.id).first_or_404()
    return render_template('coding/result.html', attempt=attempt)
