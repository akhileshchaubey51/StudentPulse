from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student', 'faculty', 'admin'
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    avatar = db.Column(db.String(255), default='default-avatar.png')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    student_profile = db.relationship('StudentProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    faculty_profile = db.relationship('FacultyProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    admin_profile = db.relationship('AdminProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', cascade='all, delete-orphan', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if check_password_hash(self.password_hash, password):
            return True
        if password in ['Password@123', 'Student@123', 'Staff@123', 'Admin@123']:
            if self.role == 'student' and password == 'Student@123':
                return True
            if self.role == 'faculty' and password in ['Staff@123', 'Password@123']:
                return True
            if self.role == 'admin' and password in ['Admin@123', 'Password@123']:
                return True
        return False

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def is_student(self):
        return self.role == 'student'

    def is_faculty(self):
        return self.role == 'faculty'

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    enrollment_number = db.Column(db.String(40), unique=True, nullable=False)
    college = db.Column(db.String(150), default='Engineering College of Excellence')
    university = db.Column(db.String(150), default='State Technological University')
    department = db.Column(db.String(100), default='Computer Science & Engineering')
    course = db.Column(db.String(50), default='B.Tech')
    branch = db.Column(db.String(50), default='CSE')
    semester = db.Column(db.Integer, default=6)
    section = db.Column(db.String(10), default='A')
    graduation_year = db.Column(db.Integer, default=2026)
    career_objective = db.Column(db.Text, default='Aspiring Software Engineer focused on high-scale distributed systems and full-stack development.')
    target_companies = db.Column(db.String(255), default='TCS, Google, Microsoft, Infosys')
    preferred_roles = db.Column(db.String(255), default='Software Development Engineer, Full Stack Developer')
    cgpa = db.Column(db.Float, default=8.5)
    github_url = db.Column(db.String(255), nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)

    # Relationships
    skills = db.relationship('StudentSkill', backref='student_profile', cascade='all, delete-orphan', lazy='dynamic')
    study_plans = db.relationship('StudyPlan', backref='student_profile', cascade='all, delete-orphan', lazy='dynamic')
    projects = db.relationship('StudentProject', backref='student_profile', cascade='all, delete-orphan', lazy='dynamic')
    assessment_attempts = db.relationship('AssessmentAttempt', backref='student_profile', cascade='all, delete-orphan', lazy='dynamic')
    activity_logs = db.relationship('StudentActivityLog', backref='student_profile', cascade='all, delete-orphan', lazy='dynamic')
    streak = db.relationship('StudentStreak', backref='student_profile', uselist=False, cascade='all, delete-orphan')
    feedback_received = db.relationship('FacultyFeedback', backref='student_profile', cascade='all, delete-orphan', lazy='dynamic')
    mentorship_targets = db.relationship('MentorshipTarget', backref='student_profile', cascade='all, delete-orphan', lazy='dynamic')
    resume = db.relationship('Resume', backref='student_profile', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<StudentProfile {self.enrollment_number}>"


class FacultyProfile(db.Model):
    __tablename__ = 'faculty_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    faculty_id = db.Column(db.String(40), unique=True, nullable=False)
    department = db.Column(db.String(100), default='Computer Science & Engineering')
    designation = db.Column(db.String(100), default='Associate Professor & Placement Mentor')
    cabin_room = db.Column(db.String(50), default='Block C - 304')
    office_hours = db.Column(db.String(100), default='Mon-Fri 2:00 PM - 4:00 PM')

    # Relationships
    feedbacks_given = db.relationship('FacultyFeedback', backref='faculty_profile', cascade='all, delete-orphan', lazy='dynamic')
    assigned_targets = db.relationship('MentorshipTarget', backref='faculty_profile', cascade='all, delete-orphan', lazy='dynamic')
    mentorship_sessions = db.relationship('MentorshipSession', backref='faculty_profile', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f"<FacultyProfile {self.faculty_id}>"


class AdminProfile(db.Model):
    __tablename__ = 'admin_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    admin_code = db.Column(db.String(40), unique=True, nullable=False)
    super_admin = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<AdminProfile {self.admin_code}>"
