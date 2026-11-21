from datetime import datetime
import json
from extensions import db

class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # 'DSA', 'Python', 'Java', 'SQL', 'Aptitude', 'Logical', 'Verbal'
    sub_topic = db.Column(db.String(100), default='General')
    difficulty = db.Column(db.String(20), default='Medium')  # Easy, Medium, Hard
    question_text = db.Column(db.Text, nullable=False)
    options_json = db.Column(db.Text, nullable=False)  # JSON list of strings
    correct_option = db.Column(db.Integer, nullable=False)  # 0, 1, 2, 3
    explanation = db.Column(db.Text, nullable=True)

    def get_options(self):
        try:
            return json.loads(self.options_json)
        except Exception:
            return []


class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'DSA', 'Coding', 'Aptitude', 'Language'
    duration_minutes = db.Column(db.Integer, default=20)
    passing_score = db.Column(db.Integer, default=60)  # Percentage
    total_marks = db.Column(db.Integer, default=100)
    is_active = db.Column(db.Boolean, default=True)

    questions = db.relationship('AssessmentQuestion', backref='assessment', cascade='all, delete-orphan')
    attempts = db.relationship('AssessmentAttempt', backref='assessment', cascade='all, delete-orphan')


class AssessmentQuestion(db.Model):
    __tablename__ = 'assessment_questions'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    points = db.Column(db.Integer, default=10)

    question = db.relationship('Question')


class AssessmentAttempt(db.Model):
    __tablename__ = 'assessment_attempts'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=10)
    correct_answers = db.Column(db.Integer, default=0)
    time_taken_seconds = db.Column(db.Integer, default=0)
    passed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship('AssessmentAnswer', backref='attempt', cascade='all, delete-orphan')


class AssessmentAnswer(db.Model):
    __tablename__ = 'assessment_answers'

    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('assessment_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    selected_option = db.Column(db.Integer, nullable=True)
    is_correct = db.Column(db.Boolean, default=False)

    question = db.relationship('Question')
