from datetime import datetime
import json
from extensions import db

class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), unique=True, nullable=False)
    template_name = db.Column(db.String(50), default='Classic Tech')
    summary = db.Column(db.Text, nullable=True)
    certifications_json = db.Column(db.Text, default='[]')
    achievements_json = db.Column(db.Text, default='[]')
    experience_json = db.Column(db.Text, default='[]')
    additional_info = db.Column(db.Text, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_certifications(self):
        try:
            return json.loads(self.certifications_json)
        except Exception:
            return []

    def get_achievements(self):
        try:
            return json.loads(self.achievements_json)
        except Exception:
            return []

    def get_experience(self):
        try:
            return json.loads(self.experience_json)
        except Exception:
            return []
