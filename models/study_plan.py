from datetime import datetime, date
from extensions import db

class StudyPlan(db.Model):
    __tablename__ = 'study_plans'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    target_company = db.Column(db.String(100), nullable=True)
    target_role = db.Column(db.String(100), nullable=True)
    plan_type = db.Column(db.String(50), default='Placement Roadmap')  # Daily, Weekly, Roadmap
    start_date = db.Column(db.Date, default=date.today)
    target_date = db.Column(db.Date, nullable=True)
    weekly_hours = db.Column(db.Integer, default=14)
    ai_generated = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(30), default='Active')  # Active, Completed, Paused
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    tasks = db.relationship('StudyTask', backref='study_plan', cascade='all, delete-orphan', lazy='dynamic')

    def progress_percentage(self):
        total = self.tasks.count()
        if total == 0:
            return 0
        completed = self.tasks.filter_by(is_completed=True).count()
        return int((completed / total) * 100)

    def __repr__(self):
        return f"<StudyPlan {self.title}>"


class StudyTask(db.Model):
    __tablename__ = 'study_tasks'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('study_plans.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    skill_name = db.Column(db.String(100), default='General')
    topic = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration_minutes = db.Column(db.Integer, default=45)
    priority = db.Column(db.String(20), default='High')  # High, Medium, Low
    scheduled_date = db.Column(db.Date, default=date.today)
    deadline = db.Column(db.Date, nullable=True)
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    resources = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"<StudyTask {self.title} (Done={self.is_completed})>"
