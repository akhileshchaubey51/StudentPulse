from datetime import datetime, date, timedelta
import json
from app import create_app
from extensions import db
from models.user import User, StudentProfile, FacultyProfile, AdminProfile
from models.academic import Department, Course, Semester, Batch, Section, StudentBatchAssignment, FacultyBatchAssignment, FacultyStudentAssignment
from models.skill import Skill, StudentSkill
from models.company import Company, JobRole, JobRoleSkill
from models.campus_drive import CampusDrive, DriveApplication
from models.study_plan import StudyPlan, StudyTask
from models.project import StudentProject, ProjectMilestone
from models.assessment import Question, Assessment, AssessmentQuestion, AssessmentAttempt, AssessmentAnswer
from models.interview import InterviewQuestion
from models.resume import Resume
from models.faculty import FacultyFeedback, MentorshipTarget
from models.activity import StudentActivityLog, StudentStreak
from models.notification import Notification

from seed_official import seed_official_database

def seed_database():
    seed_official_database()

if __name__ == '__main__':
    seed_database()

        print("1. Creating Academic Structure Across Programs (B.Tech, BCA, MCA, B.Pharma, MBA)...")
        # Departments
        cse_dept = Department(name='Computer Science & Engineering', code='CSE', description='Core software engineering and systems')
        it_dept = Department(name='Information Technology', code='IT', description='Information infrastructure and web systems')
        ca_dept = Department(name='Computer Applications', code='DOCA', description='Software development, applications, and web tech')
        pharma_dept = Department(name='Pharmaceutical Sciences', code='PHARMA', description='Medicinal chemistry, pharmacology, and drug discovery')
        mgmt_dept = Department(name='School of Business & Management', code='DOMS', description='Finance, analytics, marketing, and leadership')
        db.session.add_all([cse_dept, it_dept, ca_dept, pharma_dept, mgmt_dept])
        db.session.flush()

        # Courses
        btech_cse = Course(department_id=cse_dept.id, name='Bachelor of Technology in CSE', code='BTECH-CSE', total_semesters=8)
        bca_course = Course(department_id=ca_dept.id, name='Bachelor of Computer Applications', code='BCA', total_semesters=6)
        mca_course = Course(department_id=ca_dept.id, name='Master of Computer Applications', code='MCA', total_semesters=4)
        bpharma_course = Course(department_id=pharma_dept.id, name='Bachelor of Pharmacy', code='BPHARMA', total_semesters=8)
        mba_course = Course(department_id=mgmt_dept.id, name='Master of Business Administration', code='MBA', total_semesters=4)
        db.session.add_all([btech_cse, bca_course, mca_course, bpharma_course, mba_course])
        db.session.flush()

        sem6 = Semester(course_id=btech_cse.id, number=6, academic_year='2025-2026')
        db.session.add(sem6)
        db.session.flush()

        batch_2026 = Batch(semester_id=sem6.id, name='Class of 2026 - All Programs', graduation_year=2026)
        db.session.add(batch_2026)
        db.session.flush()

        sec_a = Section(batch_id=batch_2026.id, name='Section A')
        sec_b = Section(batch_id=batch_2026.id, name='Section B')
        db.session.add_all([sec_a, sec_b])
        db.session.flush()

        print("2. Creating Comprehensive Skills Catalog (Tech, Pharmacy, Business, Soft Skills)...")
        skills_data = [
            # Technical / IT (B.Tech, BCA, MCA)
            ('Python', 'Technical', 'Programming', 'High-level language for backend, automation, and AI.'),
            ('Java', 'Technical', 'Programming', 'Enterprise object-oriented programming language.'),
            ('Data Structures and Algorithms', 'Technical', 'Core CS', 'Arrays, Trees, Graphs, DP, and algorithms.'),
            ('SQL', 'Technical', 'Database', 'Relational database queries, normalization, and optimization.'),
            ('OOPS', 'Technical', 'Core CS', 'Object-Oriented Design principles and clean architecture.'),
            ('DBMS', 'Technical', 'Database', 'Transactions, ACID properties, and relational storage.'),
            ('Web Development', 'Technical', 'Frontend/Backend', 'HTML, CSS, JavaScript, and REST APIs.'),
            # Pharmacy & Life Sciences (B.Pharma)
            ('Pharmacology', 'Technical', 'Pharmacy', 'Drug actions, mechanisms, therapeutic effects, and toxicity.'),
            ('Pharmaceutics & Formulation', 'Technical', 'Pharmacy', 'Drug formulation, dosage delivery, and stability.'),
            ('Clinical Research & GCP', 'Technical', 'Pharmacy', 'Clinical trial phases, documentation, and Good Clinical Practice.'),
            ('Pharmacovigilance', 'Technical', 'Pharmacy', 'Adverse drug reaction monitoring and drug safety regulations.'),
            ('Medicinal Chemistry', 'Technical', 'Pharmacy', 'Structure-activity relationship and pharmaceutical analysis.'),
            # Business & Management (BBA, MBA)
            ('Financial Analysis', 'Non-Technical', 'Management', 'Corporate valuation, balance sheets, and budgeting.'),
            ('Market Research & Strategy', 'Non-Technical', 'Management', 'Competitive intelligence and product positioning.'),
            # Universal Aptitude & Soft Skills
            ('Communication', 'Non-Technical', 'Soft Skills', 'Professional articulation and presentation skills.'),
            ('Problem Solving', 'Non-Technical', 'Aptitude', 'Structured quantitative and analytical reasoning.'),
            ('Logical Reasoning', 'Non-Technical', 'Aptitude', 'Deductive logic, patterns, and critical reasoning.')
        ]

        skill_records = {}
        for name, cat, sub_cat, desc in skills_data:
            s = Skill(name=name, category=cat, sub_category=sub_cat, description=desc)
            db.session.add(s)
            db.session.flush()
            skill_records[name] = s

        print("3. Creating Companies Across Tech, Pharma, and Consulting...")
        # TCS (Tech / BCA / MCA / BTech)
        tcs = Company(
            name='TCS (Tata Consultancy Services)',
            description='Global IT enterprise hiring across B.Tech, BCA, MCA, and graduate programs annually.',
            website='https://www.tcs.com',
            careers_url='https://www.tcs.com/careers',
            tier='Tier 1 Service',
            is_verified=True,
            last_verified_date=date.today()
        )
        db.session.add(tcs)
        db.session.flush()

        tcs_role = JobRole(
            company_id=tcs.id,
            title='Software Engineer & Developer (TCS Digital / Ninja)',
            description='Software engineering, cloud apps, and modern digital development.',
            ctc_range='3.6 - 7.5 LPA',
            min_cgpa=6.0,
            selection_process='TCS NQT (Aptitude + Foundation Coding) -> Technical Round -> HR'
        )
        db.session.add(tcs_role)

        # Sun Pharma (Pharma / B.Pharma)
        sun_pharma = Company(
            name='Sun Pharmaceutical Industries',
            description='Leading international pharmaceutical company specializing in formulations, active ingredients, and clinical trials.',
            website='https://www.sunpharma.com',
            careers_url='https://www.sunpharma.com/careers',
            tier='Pharma & Healthcare Leader',
            is_verified=True,
            last_verified_date=date.today()
        )
        db.session.add(sun_pharma)
        db.session.flush()

        sun_role = JobRole(
            company_id=sun_pharma.id,
            title='Executive Trainee - Quality Assurance & Pharmacovigilance',
            description='Drug quality analysis, regulatory compliance, and post-market safety surveillance.',
            ctc_range='4.2 - 6.8 LPA',
            min_cgpa=6.5,
            selection_process='Domain Technical Test (Pharmacology) -> Technical Panel -> HR'
        )
        db.session.add(sun_role)

        # Deloitte (Consulting / BTech / BCA / MCA / MBA)
        deloitte = Company(
            name='Deloitte',
            description='Big 4 professional services giant offering technology consulting, analytics, and business transformation.',
            website='https://www.deloitte.com',
            careers_url='https://www2.deloitte.com/careers',
            tier='Global Consulting',
            is_verified=True,
            last_verified_date=date.today()
        )
        db.session.add(deloitte)
        db.session.flush()

        deloitte_role = JobRole(
            company_id=deloitte.id,
            title='Associate Analyst & Business Technology Consultant',
            description='Work with global Fortune 500 clients on technology modernization, cloud, and business solutions.',
            ctc_range='7.5 - 12.0 LPA',
            min_cgpa=6.8,
            selection_process='Aptitude Assessment -> Case Study Round -> Partner Interview'
        )
        db.session.add(deloitte_role)

        # Google
        google = Company(
            name='Google',
            description='Global technology innovator in cloud, distributed systems, web platforms, and machine learning.',
            website='https://careers.google.com',
            careers_url='https://careers.google.com',
            tier='Product & Big Tech',
            is_verified=True,
            last_verified_date=date.today()
        )
        db.session.add(google)
        db.session.flush()

        google_role = JobRole(
            company_id=google.id,
            title='Associate Software Engineer (Campus Graduate)',
            description='Develop, test, and maintain high-scale global software systems.',
            ctc_range='22.0 - 35.0 LPA',
            min_cgpa=7.5,
            selection_process='Online Assessment -> 3 Technical DSA / Architecture Rounds -> Googleyness'
        )
        db.session.add(google_role)
        db.session.commit()

        print("4. Creating Live Campus Placement Drives (All Programs)...")
        drive1 = CampusDrive(
            company_id=tcs.id,
            title='Campus Recruitment 2026 - Ninja & Digital Tracks',
            eligible_courses='B.Tech, BCA, MCA',
            eligible_branches='Computer Science, IT, Computer Applications',
            min_cgpa=6.0,
            package_ctc='3.6 - 7.5 LPA',
            drive_date=date.today() + timedelta(days=20),
            last_date_to_apply=date.today() + timedelta(days=12),
            job_location='Pan India / Hybrid',
            description='Open to final year B.Tech, BCA, and MCA students. Tests foundational problem solving and technical concepts.',
            selection_process='1. NQT Online Test\n2. Technical Interview\n3. HR Round',
            status='Active'
        )

        drive2 = CampusDrive(
            company_id=sun_pharma.id,
            title='Graduate Campus Hiring - QA, QC & Pharmacovigilance',
            eligible_courses='B.Pharma, M.Pharma',
            eligible_branches='Pharmaceutical Sciences',
            min_cgpa=6.5,
            package_ctc='4.5 - 6.5 LPA',
            drive_date=date.today() + timedelta(days=25),
            last_date_to_apply=date.today() + timedelta(days=15),
            job_location='Vadodara / Mumbai / Baddi Plant',
            description='Opportunities in formulation development, stability testing, and regulatory documentation for Pharmacy graduates.',
            selection_process='1. Pharma Domain MCQ Test\n2. Technical Panel Interview\n3. HR Discussion',
            status='Active'
        )

        drive3 = CampusDrive(
            company_id=deloitte.id,
            title='Campus Consulting & Technology Analyst 2026',
            eligible_courses='B.Tech, BCA, MCA, MBA',
            eligible_branches='All Eligible Disciplines',
            min_cgpa=7.0,
            package_ctc='8.0 - 11.5 LPA',
            drive_date=date.today() + timedelta(days=30),
            last_date_to_apply=date.today() + timedelta(days=18),
            job_location='Bengaluru / Hyderabad / Gurugram',
            description='Prestigious consulting opportunity working across cloud, enterprise architecture, and financial technology consulting.',
            selection_process='1. Cognitive & Verbal Assessment\n2. Case Study Interview\n3. Partner Interview',
            status='Active'
        )
        db.session.add_all([drive1, drive2, drive3])
        db.session.commit()

        print("5. Creating Users for All Portals...")
        # Admin
        admin_user = User(email='admin@studentpulse.edu', first_name='Evelyn', last_name='Vance', role='admin', is_active=True)
        admin_user.set_password('Admin@123')
        db.session.add(admin_user)
        db.session.flush()
        db.session.add(AdminProfile(user_id=admin_user.id, admin_code='ADM-2026-001', super_admin=True))

        # Faculty Mentor
        faculty_user = User(email='prof.sharma@studentpulse.edu', first_name='Dr. Rajesh', last_name='Sharma', role='faculty', is_active=True)
        faculty_user.set_password('Faculty@123')
        db.session.add(faculty_user)
        db.session.flush()

        faculty_prof = FacultyProfile(
            user_id=faculty_user.id,
            faculty_id='FAC-CSE-042',
            department='Computer Science & Engineering',
            designation='Professor & Training-Placement Incharge',
            cabin_room='Academic Block B, Room 310'
        )
        db.session.add(faculty_prof)
        db.session.flush()

        # Assign faculty to batch
        db.session.add(FacultyBatchAssignment(faculty_id=faculty_prof.id, batch_id=batch_2026.id))

        # Student (Alex Rivera)
        student_user = User(email='alex.student@studentpulse.edu', first_name='Alex', last_name='Rivera', role='student', is_active=True)
        student_user.set_password('Student@123')
        db.session.add(student_user)
        db.session.flush()

        student_prof = StudentProfile(
            user_id=student_user.id,
            enrollment_number='EN22CS1045',
            college='Institute of Advanced Technology & Engineering',
            university='State Technological University',
            department='Computer Science & Engineering',
            course='B.Tech',
            branch='CSE',
            semester=6,
            section='A',
            graduation_year=2026,
            cgpa=8.65,
            career_objective='Motivated full-stack developer and problem solver aspiring for a top software development or consulting career.',
            target_companies='TCS, Sun Pharma, Deloitte, Google',
            preferred_roles='Software Engineer, Technology Analyst',
            github_url='https://github.com/alexrivera-tech',
            linkedin_url='https://linkedin.com/in/alexrivera-tech'
        )
        db.session.add(student_prof)
        db.session.flush()

        # Assignments
        db.session.add(StudentBatchAssignment(student_id=student_prof.id, batch_id=batch_2026.id, section_id=sec_a.id))
        db.session.add(FacultyStudentAssignment(faculty_id=faculty_prof.id, student_id=student_prof.id))

        # Pre-seed one drive application for Alex (Applied to TCS)
        db.session.add(DriveApplication(drive_id=drive1.id, student_id=student_prof.id, status='Applied'))

        print("6. Creating Student Tracked Skills...")
        student_skills_data = [
            ('Python', 'Intermediate', 'Learning', 70, 75, True),
            ('Java', 'Intermediate', 'Learning', 68, 70, True),
            ('Data Structures and Algorithms', 'Basic', 'Learning', 50, 55, False),
            ('SQL', 'Intermediate', 'Learning', 75, 80, True),
            ('OOPS', 'Intermediate', 'Mastered', 80, 85, True),
            ('Web Development', 'Advanced', 'Mastered', 85, 82, True),
            ('Problem Solving', 'Intermediate', 'Learning', 65, 60, False),
            ('Communication', 'Advanced', 'Mastered', 85, 80, False)
        ]
        for name, prof, status, self_s, assess_s, ver in student_skills_data:
            if name in skill_records:
                db.session.add(StudentSkill(
                    student_id=student_prof.id,
                    skill_id=skill_records[name].id,
                    proficiency=prof,
                    learning_status=status,
                    self_score=self_s,
                    assessment_score=assess_s,
                    is_verified=ver,
                    last_updated=datetime.utcnow() - timedelta(days=2)
                ))

        print("7. Creating Question Bank & Mock Tests...")
        q1 = Question(
            category='DSA', sub_topic='Trees', difficulty='Medium',
            question_text='Which traversal of a Binary Search Tree (BST) produces elements in strictly sorted ascending order?',
            options_json=json.dumps(['Pre-order Traversal', 'In-order Traversal', 'Post-order Traversal', 'Level-order Traversal']),
            correct_option=1, explanation='In-order traversal visits left subtree, root, then right subtree, producing ascending sorted keys in BST.'
        )
        q2 = Question(
            category='Python', sub_topic='Core', difficulty='Easy',
            question_text='What does the bool() function return for an empty list [] in Python?',
            options_json=json.dumps(['True', 'False', 'None', 'SyntaxError']),
            correct_option=1, explanation='In Python, empty sequences evaluate to False in a boolean context.'
        )
        q3 = Question(
            category='SQL', sub_topic='Aggregation', difficulty='Medium',
            question_text='Which clause is used in SQL to filter rows AFTER grouping with GROUP BY?',
            options_json=json.dumps(['WHERE', 'HAVING', 'ORDER BY', 'PARTITION BY']),
            correct_option=1, explanation='HAVING filters groups created by GROUP BY. WHERE filters rows before grouping.'
        )
        q4 = Question(
            category='Aptitude', sub_topic='Quantitative', difficulty='Easy',
            question_text='A train travels at 72 km/h. How many meters does it cover in 10 seconds?',
            options_json=json.dumps(['150 meters', '180 meters', '200 meters', '250 meters']),
            correct_option=2, explanation='72 km/h = 72 * (5/18) = 20 m/s. In 10 seconds: 20 * 10 = 200 meters.'
        )
        db.session.add_all([q1, q2, q3, q4])
        db.session.flush()

        test1 = Assessment(title='Placement Readiness Diagnostic Assessment', category='DSA', duration_minutes=20, passing_score=60)
        db.session.add(test1)
        db.session.flush()

        for q in [q1, q2, q3, q4]:
            db.session.add(AssessmentQuestion(assessment_id=test1.id, question_id=q.id, points=25))

        print("8. Creating Personalized Study Plan & Project...")
        plan = StudyPlan(
            student_id=student_prof.id,
            title='Campus Placement Sprint 2026',
            target_company='TCS / Deloitte',
            target_role='Software Engineer & Consultant',
            weekly_hours=14,
            start_date=date.today() - timedelta(days=5),
            target_date=date.today() + timedelta(days=25),
            ai_generated=True,
            status='Active'
        )
        db.session.add(plan)
        db.session.flush()

        db.session.add(StudyTask(plan_id=plan.id, student_id=student_prof.id, title='Java Collections & Memory Internals', skill_name='Java', topic='Collections', duration_minutes=60, priority='High', scheduled_date=date.today()-timedelta(days=2), is_completed=True, completed_at=datetime.utcnow()-timedelta(days=2)))
        db.session.add(StudyTask(plan_id=plan.id, student_id=student_prof.id, title='SQL Joins, Subqueries & Indexing', skill_name='SQL', topic='Joins', duration_minutes=45, priority='High', scheduled_date=date.today()-timedelta(days=1), is_completed=True, completed_at=datetime.utcnow()-timedelta(days=1)))
        db.session.add(StudyTask(plan_id=plan.id, student_id=student_prof.id, title='Binary Search Tree Traversals & Practice', skill_name='Data Structures and Algorithms', topic='Trees', duration_minutes=60, priority='High', scheduled_date=date.today(), is_completed=False))

        proj = StudentProject(
            student_id=student_prof.id,
            title='Student Pulse: Unified Campus Placement Platform',
            description='Production web application connecting students, placement cells, and recruiters with skill gap analysis and live drive tracking.',
            category='Academic Capstone',
            tech_stack='Python, Flask, SQLite, Bootstrap, Chart.js',
            github_url='https://github.com/alexrivera-tech/student-pulse',
            progress_percentage=75,
            status='In Progress'
        )
        db.session.add(proj)
        db.session.flush()
        db.session.add(ProjectMilestone(project_id=proj.id, title='Architecture & Multi-Course Database Setup', is_completed=True, completed_at=datetime.utcnow()-timedelta(days=10)))
        db.session.add(ProjectMilestone(project_id=proj.id, title='Campus Placement Drives & Application Engine', is_completed=True, completed_at=datetime.utcnow()-timedelta(days=2)))

        print("9. Creating Historical Activity Logs for Heatmap & 14-Day Streak...")
        today = date.today()
        for i in range(13, -1, -1):
            act_date = today - timedelta(days=i)
            db.session.add(StudentActivityLog(
                student_id=student_prof.id,
                activity_type='study_task',
                activity_title=f"Study Session: Concept Preparation Day {14-i}",
                activity_date=act_date,
                duration_minutes=45,
                status='completed'
            ))

        db.session.add(StudentStreak(
            student_id=student_prof.id,
            current_streak=14,
            longest_streak=18,
            total_active_days=28,
            last_active_date=today,
            updated_at=datetime.utcnow()
        ))

        # Notification
        db.session.add(Notification(
            user_id=student_user.id,
            title="New Campus Hiring Drive: TCS",
            message="Campus Recruitment 2026 is now open for your program. Check eligibility and apply!",
            category="success",
            link="/drives/"
        ))

        db.session.commit()
        print("Database Initialized and Seeded Successfully!")
        print("-----------------------------------------------------------------")
        print("Test Logins:")
        print("Student (B.Tech / Tech):  alex.student@studentpulse.edu / Student@123")
        print("Faculty (Cohort Mentor):  prof.sharma@studentpulse.edu / Faculty@123")
        print("Admin (Placement Cell):   admin@studentpulse.edu / Admin@123")
        print("-----------------------------------------------------------------")

if __name__ == '__main__':
    seed_database()
