from datetime import datetime
from extensions import db

class InterviewQuestion(db.Model):
    __tablename__ = 'interview_questions'

    id = db.Column(db.Integer, primary_key=True)
    role_category = db.Column(db.String(50), default='Software Engineer')
    question_type = db.Column(db.String(20), default='Technical')  # Technical, HR, Behavioral
    skill_topic = db.Column(db.String(100), default='General')
    question_text = db.Column(db.Text, nullable=False)
    key_points = db.Column(db.Text, nullable=True)
    sample_answer = db.Column(db.Text, nullable=True)


class MockInterview(db.Model):
    __tablename__ = 'mock_interviews'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    target_role = db.Column(db.String(100), default='Software Engineer')
    target_company = db.Column(db.String(100), default='TCS')
    interview_type = db.Column(db.String(30), default='Technical')
    score = db.Column(db.Integer, default=75)
    overall_feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    responses = db.relationship('InterviewResponse', backref='mock_interview', cascade='all, delete-orphan')
    student = db.relationship('StudentProfile', backref=db.backref('mock_interviews', lazy='dynamic'))


class InterviewResponse(db.Model):
    __tablename__ = 'interview_responses'

    id = db.Column(db.Integer, primary_key=True)
    mock_interview_id = db.Column(db.Integer, db.ForeignKey('mock_interviews.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('interview_questions.id'), nullable=False)
    student_answer = db.Column(db.Text, nullable=False)
    ai_feedback = db.Column(db.Text, nullable=True)
    score = db.Column(db.Integer, default=70)

    question = db.relationship('InterviewQuestion')
