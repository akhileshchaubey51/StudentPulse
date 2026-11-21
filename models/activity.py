from datetime import datetime, date
from extensions import db

class StudentActivityLog(db.Model):
    __tablename__ = 'student_activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False, index=True)
    activity_type = db.Column(db.String(50), nullable=False)  # 'study_task', 'coding_quiz', 'skill_assessment', 'project_milestone', 'interview_mock', 'learning_session'
    activity_title = db.Column(db.String(200), nullable=False)
    activity_date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    duration_minutes = db.Column(db.Integer, default=30)
    related_record_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='completed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ActivityLog {self.student_id}: {self.activity_title} on {self.activity_date}>"


class StudentStreak(db.Model):
    __tablename__ = 'student_streaks'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), unique=True, nullable=False)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    total_active_days = db.Column(db.Integer, default=0)
    last_active_date = db.Column(db.Date, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Streak student={self.student_id} current={self.current_streak} max={self.longest_streak}>"
