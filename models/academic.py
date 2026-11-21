from datetime import datetime
from extensions import db

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    courses = db.relationship('Course', backref='department', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Department {self.code}>"


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)
    total_semesters = db.Column(db.Integer, default=8)

    semesters = db.relationship('Semester', backref='course', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Course {self.code}>"


class Semester(db.Model):
    __tablename__ = 'semesters'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    academic_year = db.Column(db.String(20), default='2025-2026')

    batches = db.relationship('Batch', backref='semester', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Semester {self.number} ({self.academic_year})>"


class Batch(db.Model):
    __tablename__ = 'batches'

    id = db.Column(db.Integer, primary_key=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.Integer, nullable=False)

    sections = db.relationship('Section', backref='batch', cascade='all, delete-orphan')
    student_assignments = db.relationship('StudentBatchAssignment', backref='batch', cascade='all, delete-orphan')
    faculty_assignments = db.relationship('FacultyBatchAssignment', backref='batch', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Batch {self.name}>"


class Section(db.Model):
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    name = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<Section {self.name}>"


class StudentBatchAssignment(db.Model):
    __tablename__ = 'student_batch_assignments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('StudentProfile', backref='batch_assignments')
    section = db.relationship('Section')


class FacultyBatchAssignment(db.Model):
    __tablename__ = 'faculty_batch_assignments'

    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty_profiles.id'), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    faculty = db.relationship('FacultyProfile', backref='batch_assignments')


class FacultyStudentAssignment(db.Model):
    __tablename__ = 'faculty_student_assignments'

    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty_profiles.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student_profiles.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    faculty = db.relationship('FacultyProfile', backref='student_assignments')
    student = db.relationship('StudentProfile', backref='faculty_assignment')
