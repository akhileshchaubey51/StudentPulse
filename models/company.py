from datetime import datetime
from extensions import db

class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    logo = db.Column(db.String(255), default='default-company.png')
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(255), nullable=True)
    careers_url = db.Column(db.String(255), nullable=True)
    source_url = db.Column(db.String(255), nullable=True)
    last_verified_date = db.Column(db.Date, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=True)
    industry = db.Column(db.String(100), default='Information Technology')
    tier = db.Column(db.String(30), default='Tier 1')  # Tier 1, Product, Mass, Startup

    job_roles = db.relationship('JobRole', backref='company', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Company {self.name}>"


class JobRole(db.Model):
    __tablename__ = 'job_roles'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    min_cgpa = db.Column(db.Float, default=6.5)
    graduation_years = db.Column(db.String(100), default='2025, 2026')
    experience_level = db.Column(db.String(50), default='Entry Level / Fresher')
    ctc_range = db.Column(db.String(50), default='4.0 - 9.0 LPA')
    assessment_pattern = db.Column(db.Text, default='Round 1: Online Aptitude & Coding\nRound 2: Technical Interview\nRound 3: HR / Managerial')
    selection_process = db.Column(db.Text, default='Aptitude -> Coding -> Technical -> HR')
    is_active = db.Column(db.Boolean, default=True)

    required_skills = db.relationship('JobRoleSkill', backref='job_role', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<JobRole {self.title} at {self.company_id}>"


class JobRoleSkill(db.Model):
    __tablename__ = 'job_role_skills'

    id = db.Column(db.Integer, primary_key=True)
    job_role_id = db.Column(db.Integer, db.ForeignKey('job_roles.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    is_required = db.Column(db.Boolean, default=True)  # True = Must have, False = Preferred
    minimum_proficiency = db.Column(db.String(30), default='Intermediate')  # Beginner, Basic, Intermediate, Advanced, Expert
    weight = db.Column(db.Integer, default=5)  # 1 to 10 importance

    skill = db.relationship('Skill')
