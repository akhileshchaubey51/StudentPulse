from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime
from extensions import db
from models.interview import InterviewQuestion, MockInterview, InterviewResponse
from services.ai_service import AIService
from services.activity_service import log_activity

interviews_bp = Blueprint('interviews', __name__, url_prefix='/interviews')

@interviews_bp.route('/')
@login_required
def index():
    profile = current_user.student_profile if current_user.is_student() else None

    q_type = request.args.get('type', 'all')
    topic = request.args.get('topic', 'all')

    query = InterviewQuestion.query
    if q_type != 'all':
        query = query.filter_by(question_type=q_type)
    if topic != 'all':
        query = query.filter_by(skill_topic=topic)

    questions = query.all()
    past_mocks = []
    if profile:
        past_mocks = MockInterview.query.filter_by(student_id=profile.id).order_by(MockInterview.created_at.desc()).limit(10).all()

    return render_template(
        'interviews/index.html',
        questions=questions,
        past_mocks=past_mocks,
        q_type=q_type,
        topic=topic
    )


@interviews_bp.route('/practice/<int:question_id>', methods=['GET', 'POST'])
@login_required
def practice(question_id):
    profile = current_user.student_profile if current_user.is_student() else None
    question = InterviewQuestion.query.get_or_404(question_id)

    eval_result = None
    student_ans = ""

    if request.method == 'POST':
        student_ans = request.form.get('student_answer', '').strip()
        eval_result = AIService.evaluate_interview_answer(
            question_text=question.question_text,
            student_answer=student_ans,
            key_points=question.key_points
        )

        # Create mock interview record if student profile exists
        if profile:
            mock = MockInterview(
                student_id=profile.id,
                target_role=question.role_category,
                target_company='KIET Placement Round',
                interview_type=question.question_type,
                score=eval_result['score'],
                overall_feedback=eval_result['feedback'],
                created_at=datetime.utcnow()
            )
            db.session.add(mock)
            db.session.flush()

            resp = InterviewResponse(
                mock_interview_id=mock.id,
                question_id=question.id,
                student_answer=student_ans,
                ai_feedback=eval_result['feedback'],
                score=eval_result['score']
            )
            db.session.add(resp)
            db.session.commit()

            log_activity(
                student_id=profile.id,
                activity_type='interview_mock',
                activity_title=f"Mock Interview: {question.skill_topic} ({question.question_type})",
                duration_minutes=25,
                related_record_id=mock.id
            )

            flash(f'Your response has been analyzed! Score: {eval_result["score"]}/100. Activity logged.', 'success')
        else:
            flash(f'Interview evaluation complete! Score: {eval_result["score"]}/100.', 'info')

    return render_template(
        'interviews/practice.html',
        question=question,
        eval_result=eval_result,
        student_ans=student_ans
    )
