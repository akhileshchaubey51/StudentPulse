from datetime import datetime, date
from extensions import db

class CampusDrive(db.Model):
    __tablename__ = 'campus_drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(180), nullable=False)  # e.g., "Campus Recruitment 2026 - Software Engineer & QA"
    eligible_courses = db.Column(db.String(255), default='B.Tech, BCA, MCA, B.Pharma, MBA')  # Comma separated
    eligible_branches = db.Column(db.String(255), default='All Branches')
    min_cgpa = db.Column(db.Float, default=6.0)
    package_ctc = db.Column(db.String(60), default='5.0 - 9.0 LPA')
    drive_date = db.Column(db.Date, nullable=False)
    last_date_to_apply = db.Column(db.Date, nullable=False)
    job_location = db.Column(db.String(150), default='Pan India / Hybrid')
    description = db.Column(db.Text, nullable=False)
    selection_process = db.Column(db.Text, default='1. Online Aptitude / Domain Test\n2. Technical Interview\n3. HR Round')
    application_link = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), default='Active')  # Active, Closed, Upcoming
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship('Company', backref='campus_drives')
    applications = db.relationship('DriveApplication', backref='drive', cascade='all, delete-orphan')

    def is_expired(self):
        return self.last_date_to_apply < date.today()


class DriveApplication(db.Model):
    __tablename__ = 'drive_applications'

    id = db.Column(db.Integer, primary_key=True)
    drive_id = db.Column(db.Integer, db.ForeignKey('campus_drives.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    status = db.Column(db.String(40), default='Applied')  # Applied, Shortlisted, Interview Scheduled, Selected, Rejected
    notes = db.Column(db.Text, nullable=True)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('StudentProfile', backref='drive_applications')
