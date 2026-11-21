import unittest
import os
import sys
import json
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from extensions import db
from config import Config
from models.user import User, StudentProfile, FacultyProfile, AdminProfile
from models.academic import Department, Course, Semester, Batch, Section, StudentBatchAssignment, FacultyBatchAssignment, FacultyStudentAssignment
from models.skill import Skill, StudentSkill
from models.company import Company, JobRole, JobRoleSkill
from models.study_plan import StudyPlan, StudyTask
from models.project import StudentProject, ProjectMilestone
from models.assessment import Question, Assessment, AssessmentQuestion, AssessmentAttempt
from models.faculty import FacultyFeedback, MentorshipTarget
from models.activity import StudentActivityLog, StudentStreak
from services.activity_service import log_activity, get_heatmap_data
from services.streak_service import update_student_streak
from services.ai_service import AIService

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class StudentPulseFunctionalTestSuite(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        self.seed_test_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def seed_test_data(self):
        # 1. Admin
        self.admin = User(email='admin@test.com', first_name='Admin', last_name='User', role='admin', is_active=True)
        self.admin.set_password('Admin@123')
        db.session.add(self.admin)
        db.session.flush()
        db.session.add(AdminProfile(user_id=self.admin.id, admin_code='ADM-001'))

        # 2. Faculty
        self.faculty = User(email='faculty@test.com', first_name='Rajesh', last_name='Sharma', role='faculty', is_active=True)
        self.faculty.set_password('Faculty@123')
        db.session.add(self.faculty)
        db.session.flush()
        self.faculty_prof = FacultyProfile(user_id=self.faculty.id, faculty_id='FAC-001', department='CSE')
        db.session.add(self.faculty_prof)

        # 3. Student
        self.student = User(email='student@test.com', first_name='Alex', last_name='Rivera', role='student', is_active=True)
        self.student.set_password('Student@123')
        db.session.add(self.student)
        db.session.flush()
        self.student_prof = StudentProfile(user_id=self.student.id, enrollment_number='EN001', department='CSE', graduation_year=2026)
        db.session.add(self.student_prof)
        db.session.flush()

        # Streak record
        self.streak = StudentStreak(student_id=self.student_prof.id, current_streak=0, longest_streak=0, total_active_days=0)
        db.session.add(self.streak)

        # Department & Batch
        dept = Department(name='Computer Science & Engineering', code='CSE')
        db.session.add(dept)
        db.session.flush()
        course = Course(department_id=dept.id, name='B.Tech CSE', code='BTECH')
        db.session.add(course)
        db.session.flush()
        sem = Semester(course_id=course.id, number=6)
        db.session.add(sem)
        db.session.flush()
        self.batch = Batch(semester_id=sem.id, name='Batch 2026', graduation_year=2026)
        db.session.add(self.batch)
        db.session.flush()

        # Assignments
        db.session.add(StudentBatchAssignment(student_id=self.student_prof.id, batch_id=self.batch.id))
        db.session.add(FacultyBatchAssignment(faculty_id=self.faculty_prof.id, batch_id=self.batch.id))
        db.session.add(FacultyStudentAssignment(faculty_id=self.faculty_prof.id, student_id=self.student_prof.id))

        # Skills
        self.skill_python = Skill(name='Python', category='Technical', sub_category='Programming')
        self.skill_dsa = Skill(name='Data Structures and Algorithms', category='Technical', sub_category='Core')
        self.skill_sql = Skill(name='SQL', category='Technical', sub_category='Database')
        db.session.add_all([self.skill_python, self.skill_dsa, self.skill_sql])

        # Companies
        self.company = Company(name='TCS', description='Leading IT services firm', tier='Tier 1 Service', is_verified=True)
        db.session.add(self.company)
        db.session.flush()
        self.role = JobRole(company_id=self.company.id, title='Software Engineer', ctc_range='4-7 LPA')
        db.session.add(self.role)
        db.session.flush()
        db.session.add(JobRoleSkill(job_role_id=self.role.id, skill_id=self.skill_python.id, minimum_proficiency='Intermediate', weight=8))
        db.session.add(JobRoleSkill(job_role_id=self.role.id, skill_id=self.skill_dsa.id, minimum_proficiency='Intermediate', weight=9))

        db.session.commit()

    def login(self, email, password):
        return self.client.post('/auth/login', data={'email': email, 'password': password}, follow_redirects=True)

    # ---------------------------------------------------------
    # TEST 1: AUTHENTICATION & ROLE ACCESS CONTROL
    # ---------------------------------------------------------
    def test_authentication_and_roles(self):
        # Student Login
        res_stu = self.login('student@test.com', 'Student@123')
        self.assertIn(b'Alex', res_stu.data)

        # Student trying to access admin dashboard should be forbidden (403)
        res_forbidden = self.client.get('/admin/dashboard')
        self.assertEqual(res_forbidden.status_code, 403)

        self.client.get('/auth/logout')

        # Admin Login
        res_adm = self.login('admin@test.com', 'Admin@123')
        self.assertIn(b'Administration Console', res_adm.data)

        self.client.get('/auth/logout')

        # Faculty Login
        res_fac = self.login('faculty@test.com', 'Faculty@123')
        self.assertIn(b'Faculty Mentorship', res_fac.data)

    # ---------------------------------------------------------
    # TEST 2: SKILL MANAGEMENT & LOGGING
    # ---------------------------------------------------------
    def test_student_skill_operations(self):
        self.login('student@test.com', 'Student@123')

        # Add skill
        res_add = self.client.post('/skills/add', data={
            'skill_id': self.skill_python.id,
            'proficiency': 'Intermediate',
            'learning_status': 'Learning',
            'self_score': 75
        }, follow_redirects=True)
        self.assertEqual(res_add.status_code, 200)

        stud_skill = StudentSkill.query.filter_by(student_id=self.student_prof.id, skill_id=self.skill_python.id).first()
        self.assertIsNotNone(stud_skill)
        self.assertEqual(stud_skill.proficiency, 'Intermediate')

    # ---------------------------------------------------------
    # TEST 3: ACTIVITY HEATMAP & STREAK TRACKING
    # ---------------------------------------------------------
    def test_heatmap_and_streak_calculation(self):
        today = date.today()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)

        # Log activity on two consecutive days
        log_activity(self.student_prof.id, 'study_task', 'DSA Arrays Study', duration_minutes=45, activity_date=yesterday)
        log_activity(self.student_prof.id, 'coding_quiz', 'Python Quiz', duration_minutes=30, activity_date=today)

        streak_rec = update_student_streak(self.student_prof.id)
        self.assertEqual(streak_rec.current_streak, 2)
        self.assertEqual(streak_rec.total_active_days, 2)

        # Inspect heatmap output
        heatmap = get_heatmap_data(self.student_prof.id, year=today.year)
        self.assertEqual(heatmap['total_active_days'], 2)
        self.assertEqual(heatmap['total_activities'], 2)
        self.assertGreater(heatmap['total_hours'], 1.0)

    # ---------------------------------------------------------
    # TEST 4: AI STUDY PLANNER & TASK COMPLETION
    # ---------------------------------------------------------
    def test_ai_study_planner_and_task_completion(self):
        self.login('student@test.com', 'Student@123')

        # Generate plan
        res_gen = self.client.post('/study-plans/generate', data={
            'title': 'Test Placement Sprint',
            'target_company': 'TCS',
            'target_role': 'Software Engineer',
            'weekly_hours': 14
        }, follow_redirects=True)
        self.assertEqual(res_gen.status_code, 200)

        plan = StudyPlan.query.filter_by(student_id=self.student_prof.id).first()
        self.assertIsNotNone(plan)
        self.assertGreater(plan.tasks.count(), 0)

        # Toggle first task
        task = plan.tasks.first()
        res_toggle = self.client.post(f'/study-plans/toggle-task/{task.id}', follow_redirects=True)
        self.assertEqual(res_toggle.status_code, 200)

        db.session.refresh(task)
        self.assertTrue(task.is_completed)

        # Confirm activity log was created automatically
        act = StudentActivityLog.query.filter_by(student_id=self.student_prof.id, related_record_id=task.id).first()
        self.assertIsNotNone(act)

    # ---------------------------------------------------------
    # TEST 5: FACULTY MONITORING & MENTORSHIP
    # ---------------------------------------------------------
    def test_faculty_monitoring_and_feedback(self):
        self.login('faculty@test.com', 'Faculty@123')

        # View student detail
        res_detail = self.client.get(f'/faculty/student/{self.student_prof.id}')
        self.assertEqual(res_detail.status_code, 200)
        self.assertIn(b'Alex Rivera', res_detail.data)

        # Give feedback
        res_fb = self.client.post(f'/faculty/give-feedback/{self.student_prof.id}', data={
            'feedback_text': 'Great progress on algorithms. Keep up the daily streak!',
            'category': 'Skill Improvement',
            'is_at_risk_alert': False
        }, follow_redirects=True)
        self.assertEqual(res_fb.status_code, 200)

        fb = FacultyFeedback.query.filter_by(student_id=self.student_prof.id).first()
        self.assertIsNotNone(fb)
        self.assertIn('Great progress', fb.feedback_text)

        # Assign target
        res_tgt = self.client.post(f'/faculty/assign-target/{self.student_prof.id}', data={
            'title': 'Solve 10 SQL problems',
            'target_skill': 'SQL',
            'deadline': (date.today() + timedelta(days=7)).isoformat()
        }, follow_redirects=True)
        self.assertEqual(res_tgt.status_code, 200)

        tgt = MentorshipTarget.query.filter_by(student_id=self.student_prof.id).first()
        self.assertIsNotNone(tgt)

    # ---------------------------------------------------------
    # TEST 6: ADMIN USER CREATION & GOVERNANCE
    # ---------------------------------------------------------
    def test_admin_governance(self):
        self.login('admin@test.com', 'Admin@123')

        # Create new student
        res_create = self.client.post('/admin/create-user', data={
            'first_name': 'Samantha',
            'last_name': 'Reed',
            'email': 'samantha@test.com',
            'password': 'Password@123',
            'role': 'student',
            'enrollment_number': 'EN002',
            'department': 'Computer Science & Engineering',
            'graduation_year': 2026
        }, follow_redirects=True)
        self.assertEqual(res_create.status_code, 200)

        new_user = User.query.filter_by(email='samantha@test.com').first()
        self.assertIsNotNone(new_user)
        self.assertIsNotNone(new_user.student_profile)

    # ---------------------------------------------------------
    # TEST 7: CAMPUS HIRING DRIVES (MULTI-PROGRAM)
    # ---------------------------------------------------------
    def test_campus_drives(self):
        # Admin posts a campus drive
        self.login('admin@test.com', 'Admin@123')
        res_post = self.client.post('/drives/post', data={
            'company_id': self.company.id,
            'title': 'Campus Hiring 2026',
            'courses': ['B.Tech', 'BCA', 'B.Pharma'],
            'min_cgpa': 6.0,
            'package_ctc': '5.0 LPA',
            'drive_date': (date.today() + timedelta(days=20)).isoformat(),
            'last_date_to_apply': (date.today() + timedelta(days=10)).isoformat(),
            'description': 'Open for multiple engineering & pharmacy graduates.'
        }, follow_redirects=True)
        self.assertEqual(res_post.status_code, 200)

        self.client.get('/auth/logout')

        # Student views and applies
        self.login('student@test.com', 'Student@123')
        from models.campus_drive import CampusDrive, DriveApplication
        drive = CampusDrive.query.first()
        self.assertIsNotNone(drive)

        res_apply = self.client.post(f'/drives/apply/{drive.id}', follow_redirects=True)
        self.assertEqual(res_apply.status_code, 200)

        app_record = DriveApplication.query.filter_by(drive_id=drive.id, student_id=self.student_prof.id).first()
        self.assertIsNotNone(app_record)
        self.assertEqual(app_record.status, 'Applied')

if __name__ == '__main__':
    unittest.main()
