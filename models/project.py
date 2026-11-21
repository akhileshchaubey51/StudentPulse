from datetime import datetime, date
from extensions import db

class StudentProject(db.Model):
    __tablename__ = 'student_projects'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='Academic')  # Academic, Capstone, Personal, Open-Source
    tech_stack = db.Column(db.String(255), default='Python, Flask, SQLite, HTML/CSS')
    github_url = db.Column(db.String(255), nullable=True)
    live_url = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.Date, default=date.today)
    expected_completion = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(30), default='In Progress')  # In Progress, Under Review, Completed
    progress_percentage = db.Column(db.Integer, default=20)
    submitted_for_review = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    milestones = db.relationship('ProjectMilestone', backref='project', cascade='all, delete-orphan', lazy='dynamic')
    reviews = db.relationship('ProjectReview', backref='project', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f"<StudentProject {self.title}>"


class ProjectMilestone(db.Model):
    __tablename__ = 'project_milestones'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('student_projects.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)


class ProjectReview(db.Model):
    __tablename__ = 'project_reviews'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('student_projects.id'), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty_profiles.id'), nullable=False)
    feedback = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=4)  # 1 to 5
    grade = db.Column(db.String(5), default='A')
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)

    faculty = db.relationship('FacultyProfile')
