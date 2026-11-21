from datetime import datetime
from extensions import db

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False)  # 'Technical', 'Non-Technical'
    sub_category = db.Column(db.String(50), default='Core')  # 'Programming', 'Database', 'Soft Skills', etc.
    description = db.Column(db.Text, nullable=True)
    recommended_resources = db.Column(db.Text, nullable=True)

    student_skills = db.relationship('StudentSkill', backref='skill', cascade='all, delete-orphan')
    assessments = db.relationship('SkillAssessment', backref='skill', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Skill {self.name} ({self.category})>"


class StudentSkill(db.Model):
    __tablename__ = 'student_skills'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    proficiency = db.Column(db.String(30), default='Beginner')  # Beginner, Basic, Intermediate, Advanced, Expert
    learning_status = db.Column(db.String(30), default='Learning')  # Want to Learn, Learning, Mastered
    self_score = db.Column(db.Integer, default=50)  # 0 to 100
    assessment_score = db.Column(db.Integer, default=0)  # 0 to 100 verified
    is_verified = db.Column(db.Boolean, default=False)
    evidence_url = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def numeric_proficiency(self):
        mapping = {'Beginner': 20, 'Basic': 40, 'Intermediate': 65, 'Advanced': 85, 'Expert': 100}
        return mapping.get(self.proficiency, 20)

    def __repr__(self):
        return f"<StudentSkill student={self.student_id} skill={self.skill_id} ({self.proficiency})>"


class SkillAssessment(db.Model):
    __tablename__ = 'skill_assessments'

    id = db.Column(db.Integer, primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    duration_minutes = db.Column(db.Integer, default=15)
    total_questions = db.Column(db.Integer, default=10)
    passing_score = db.Column(db.Integer, default=60)


class SkillAssessmentResult(db.Model):
    __tablename__ = 'skill_assessment_results'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('skill_assessments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    passed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
