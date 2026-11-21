from datetime import datetime, date
from extensions import db

class FacultyFeedback(db.Model):
    __tablename__ = 'faculty_feedback'

    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty_profiles.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='Skill Improvement')  # Skill Improvement, Project, Consistency, Placement
    is_at_risk_alert = db.Column(db.Boolean, default=False)
    student_response = db.Column(db.Text, nullable=True)
    response_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    faculty = db.relationship('FacultyProfile', backref='sent_feedbacks')


class MentorshipTarget(db.Model):
    __tablename__ = 'mentorship_targets'

    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty_profiles.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    title = db.Column(db.String(180), nullable=False)
    description = db.Column(db.Text, nullable=True)
    target_skill = db.Column(db.String(100), default='General')
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, In Progress, Completed, Overdue
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    faculty = db.relationship('FacultyProfile', backref='assigned_mentorship_targets')


class MentorshipSession(db.Model):
    __tablename__ = 'mentorship_sessions'

    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty_profiles.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    topic = db.Column(db.String(150), nullable=False)
    scheduled_date = db.Column(db.Date, default=date.today)
    scheduled_time = db.Column(db.String(20), default='3:00 PM')
    mode = db.Column(db.String(20), default='Offline Cabin')  # Offline Cabin, Online Meeting
    meeting_link = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Scheduled')  # Scheduled, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('StudentProfile', backref='mentorship_sessions')
    faculty = db.relationship('FacultyProfile', backref='scheduled_sessions')
