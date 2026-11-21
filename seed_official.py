import json
from datetime import datetime, date, timedelta
from app import create_app
from extensions import db
from models.user import User, StudentProfile, FacultyProfile, AdminProfile
from models.academic import Department, Course, Semester, Batch, Section, StudentBatchAssignment, FacultyBatchAssignment, FacultyStudentAssignment
from models.skill import Skill, StudentSkill
from models.company import Company, JobRole, JobRoleSkill
from models.campus_drive import CampusDrive, DriveApplication
from models.study_plan import StudyPlan, StudyTask
from models.project import StudentProject, ProjectMilestone
from models.assessment import Question, Assessment, AssessmentQuestion
from models.interview import InterviewQuestion, MockInterview, InterviewResponse
from models.faculty import FacultyFeedback, MentorshipTarget, MentorshipSession
from models.activity import StudentActivityLog, StudentStreak
from models.notification import Notification

def seed_official_database():
    app = create_app()
    with app.app_context():
        print("Cleaning and Re-initializing Student Pulse Relational Database with Official KIET Data...")
        db.drop_all()
        db.create_all()

        print("1. Creating Academic Structure (DOCA - MCA Department, CSE, IT)...")
        doca_dept = Department(name='Department of Computer Applications (MCA)', code='DOCA', description='Master of Computer Applications & Software Engineering')
        cse_dept = Department(name='Computer Science & Engineering', code='CSE', description='Core software engineering and systems')
        it_dept = Department(name='Information Technology', code='IT', description='Information infrastructure and web systems')
        db.session.add_all([doca_dept, cse_dept, it_dept])
        db.session.flush()

        mca_course = Course(department_id=doca_dept.id, name='Master of Computer Applications', code='MCA', total_semesters=4)
        btech_cse = Course(department_id=cse_dept.id, name='Bachelor of Technology in CSE', code='BTECH-CSE', total_semesters=8)
        db.session.add_all([mca_course, btech_cse])
        db.session.flush()

        sem2 = Semester(course_id=mca_course.id, number=2, academic_year='2026-2027')
        db.session.add(sem2)
        db.session.flush()

        batch_mca = Batch(semester_id=sem2.id, name='MCA Batch 2026-2028', graduation_year=2028)
        db.session.add(batch_mca)
        db.session.flush()

        sec_a = Section(batch_id=batch_mca.id, name='Section A')
        db.session.add(sec_a)
        db.session.flush()

        print("2. Creating Skills Catalog...")
        skills_data = [
            ('Python', 'Technical', 'Programming', 'Core Python, scripting, backend development, and data manipulation.'),
            ('Java', 'Technical', 'Programming', 'Enterprise object-oriented programming, JVM memory, and collections.'),
            ('Data Structures and Algorithms', 'Technical', 'Core CS', 'Arrays, Linked Lists, Trees, Graphs, DP, and asymptotic complexity.'),
            ('SQL', 'Technical', 'Database', 'Relational database querying, joins, indexing, and normalization.'),
            ('OOPS', 'Technical', 'Core CS', 'Encapsulation, inheritance, polymorphism, and abstraction design patterns.'),
            ('DBMS', 'Technical', 'Database', 'Relational storage engines, ACID transactions, and query optimization.'),
            ('Web Development', 'Technical', 'Frontend/Backend', 'HTML5, CSS3, modern JavaScript, Bootstrap, Flask REST APIs.'),
            ('Problem Solving', 'Non-Technical', 'Aptitude', 'Analytical and quantitative reasoning skills.'),
            ('Communication', 'Non-Technical', 'Soft Skills', 'Professional articulation, presentations, and technical documentation.')
        ]

        skill_records = {}
        for name, cat, sub_cat, desc in skills_data:
            s = Skill(name=name, category=cat, sub_category=sub_cat, description=desc)
            db.session.add(s)
            db.session.flush()
            skill_records[name] = s

        print("3. Creating Companies & Job Roles...")
        tcs = Company(
            name='TCS (Tata Consultancy Services)',
            description='Global IT leader hiring across MCA and engineering programs annually.',
            website='https://www.tcs.com',
            careers_url='https://www.tcs.com/careers',
            tier='Tier 1 Service',
            is_verified=True,
            last_verified_date=date.today()
        )
        deloitte = Company(
            name='Deloitte USI',
            description='Global management & technology consulting leader hiring technology analysts.',
            website='https://www.deloitte.com',
            careers_url='https://www2.deloitte.com/ui/en/careers.html',
            tier='Consulting & Strategy',
            is_verified=True,
            last_verified_date=date.today()
        )
        google = Company(
            name='Google',
            description='Global technology innovator in cloud, search, distributed systems, and AI platforms.',
            website='https://careers.google.com',
            careers_url='https://careers.google.com',
            tier='Product & Big Tech',
            is_verified=True,
            last_verified_date=date.today()
        )
        db.session.add_all([tcs, deloitte, google])
        db.session.flush()

        tcs_role = JobRole(company_id=tcs.id, title='Software Engineer (Digital & Ninja)', description='Full stack engineering, cloud and digital platforms.', ctc_range='3.6 - 7.5 LPA', min_cgpa=6.0, selection_process='NQT -> Technical -> HR')
        deloitte_role = JobRole(company_id=deloitte.id, title='Technology Analyst', description='Enterprise consulting, analytics, and software solutions.', ctc_range='8.0 - 11.5 LPA', min_cgpa=7.0, selection_process='Aptitude -> Technical -> Case Study -> HR')
        google_role = JobRole(company_id=google.id, title='Associate Software Engineer', description='High-scale distributed systems and web software development.', ctc_range='22.0 - 35.0 LPA', min_cgpa=7.5, selection_process='Coding Assessment -> 3 Technical Rounds -> Googleyness')
        db.session.add_all([tcs_role, deloitte_role, google_role])
        db.session.flush()

        print("4. Creating Campus Drives for MCA...")
        drive1 = CampusDrive(
            company_id=tcs.id,
            title='Campus Recruitment 2026-2028 - Ninja & Digital Tracks',
            eligible_courses='MCA, B.Tech',
            eligible_branches='Computer Applications, Computer Science, IT',
            min_cgpa=6.0,
            package_ctc='3.6 - 7.5 LPA',
            drive_date=date.today() + timedelta(days=20),
            last_date_to_apply=date.today() + timedelta(days=10),
            job_location='Noida / Delhi NCR / Pan India',
            description='Open to MCA students. Tests foundational problem solving and technical concepts.',
            selection_process='1. NQT Online Test\n2. Technical Interview\n3. HR Round',
            status='Active'
        )
        drive2 = CampusDrive(
            company_id=deloitte.id,
            title='Deloitte Technology Analyst Drive 2026-2028',
            eligible_courses='MCA, B.Tech',
            eligible_branches='Computer Applications, CSE, IT',
            min_cgpa=7.0,
            package_ctc='8.0 - 11.5 LPA',
            drive_date=date.today() + timedelta(days=28),
            last_date_to_apply=date.today() + timedelta(days=15),
            job_location='Gurugram / Bengaluru / Hyderabad',
            description='Consulting and technology engineering opportunities for MCA post-graduates.',
            selection_process='1. Cognitive Assessment\n2. Technical Round\n3. Partner Interview',
            status='Active'
        )
        db.session.add_all([drive1, drive2])
        db.session.flush()

        print("5. Creating the 3 Official User Accounts...")
        # 1. Admin Account
        admin_user = User(
            email='admin@kiet.edu',
            first_name='KIET',
            last_name='Administrator',
            role='admin',
            is_active=True
        )
        admin_user.set_password('Admin@123')
        db.session.add(admin_user)
        db.session.flush()
        db.session.add(AdminProfile(user_id=admin_user.id, admin_code='KIET-ADM-001', super_admin=True))

        # 2. Staff / Faculty Account
        faculty_user = User(
            email='staff@kiet.edu',
            first_name='Dr. Rajesh',
            last_name='Sharma',
            role='faculty',
            is_active=True
        )
        faculty_user.set_password('Staff@123')
        db.session.add(faculty_user)
        db.session.flush()

        faculty_prof = FacultyProfile(
            user_id=faculty_user.id,
            faculty_id='FAC-MCA-102',
            department='Department of Computer Applications (MCA)',
            designation='Associate Professor & MCA Placement Faculty Mentor',
            cabin_room='Academic Block B, MCA Wing, Room 204'
        )
        db.session.add(faculty_prof)
        db.session.flush()
        db.session.add(FacultyBatchAssignment(faculty_id=faculty_prof.id, batch_id=batch_mca.id))

        # 3. Student Account: 2628mca0206@kiet.edu
        student_user = User(
            email='2628mca0206@kiet.edu',
            first_name='Aayush',
            last_name='Sharma',
            role='student',
            is_active=True
        )
        student_user.set_password('Student@123')
        db.session.add(student_user)
        db.session.flush()

        student_prof = StudentProfile(
            user_id=student_user.id,
            enrollment_number='2628MCA0206',
            college='KIET Group of Institutions, Ghaziabad',
            university='Dr. A.P.J. Abdul Kalam Technical University (AKTU)',
            department='Department of Computer Applications (MCA)',
            course='MCA',
            branch='MCA',
            semester=2,
            section='A',
            graduation_year=2028,
            cgpa=8.75,
            career_objective='Motivated MCA scholar at KIET with strong foundation in Full Stack Development, Data Structures, and Cloud Architecture.',
            target_companies='TCS, Deloitte, Google, Infosys, Wipro',
            preferred_roles='Software Engineer, Full Stack Developer, Technology Analyst',
            github_url='https://github.com/2628mca0206-kiet',
            linkedin_url='https://linkedin.com/in/2628mca0206-kiet'
        )
        db.session.add(student_prof)
        db.session.flush()

        # Link Batch & Faculty Assignment
        db.session.add(StudentBatchAssignment(student_id=student_prof.id, batch_id=batch_mca.id, section_id=sec_a.id))
        db.session.add(FacultyStudentAssignment(faculty_id=faculty_prof.id, student_id=student_prof.id))

        # Drive Applications
        db.session.add(DriveApplication(drive_id=drive1.id, student_id=student_prof.id, status='Shortlisted'))
        db.session.add(DriveApplication(drive_id=drive2.id, student_id=student_prof.id, status='Applied'))

        # Tracked Skills
        student_skills_data = [
            ('Python', 'Advanced', 'Mastered', 88, 85, True),
            ('Java', 'Intermediate', 'Learning', 75, 78, True),
            ('Data Structures and Algorithms', 'Intermediate', 'Learning', 72, 70, False),
            ('SQL', 'Advanced', 'Mastered', 85, 90, True),
            ('OOPS', 'Advanced', 'Mastered', 85, 88, True),
            ('Web Development', 'Advanced', 'Mastered', 90, 92, True),
            ('Problem Solving', 'Intermediate', 'Learning', 76, 75, False),
            ('Communication', 'Advanced', 'Mastered', 82, 80, False)
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
                    last_updated=datetime.utcnow() - timedelta(days=1)
                ))

        print("6. Creating Questions & Practice Bank...")
        q1 = Question(
            category='DSA', sub_topic='Trees', difficulty='Medium',
            question_text='Which traversal of a Binary Search Tree (BST) produces keys in strictly ascending sorted order?',
            options_json=json.dumps(['Pre-order Traversal', 'In-order Traversal', 'Post-order Traversal', 'Level-order Traversal']),
            correct_option=1, explanation='In-order traversal visits left subtree, root, then right subtree, producing strictly ascending order.'
        )
        q2 = Question(
            category='Python', sub_topic='Core', difficulty='Easy',
            question_text='What is the output of bool([]) and bool([0]) in Python?',
            options_json=json.dumps(['False and False', 'False and True', 'True and False', 'True and True']),
            correct_option=1, explanation='An empty list evaluates to False, while a list with elements evaluates to True.'
        )
        q3 = Question(
            category='SQL', sub_topic='Queries', difficulty='Medium',
            question_text='Which clause in SQL is used to filter aggregated grouped records created by GROUP BY?',
            options_json=json.dumps(['WHERE', 'HAVING', 'ORDER BY', 'PARTITION BY']),
            correct_option=1, explanation='HAVING filters group summaries. WHERE filters before aggregation.'
        )
        db.session.add_all([q1, q2, q3])
        db.session.flush()

        test1 = Assessment(title='KIET MCA Placement Diagnostic Assessment', category='DSA', duration_minutes=25, passing_score=60)
        db.session.add(test1)
        db.session.flush()
        for q in [q1, q2, q3]:
            db.session.add(AssessmentQuestion(assessment_id=test1.id, question_id=q.id, points=25))

        # Interview Questions Seed
        iqs = [
            InterviewQuestion(role_category='Software Engineer', question_type='Technical', skill_topic='DSA', question_text='Explain how a Hash Map handles hash collisions in Java and Python internally.', sample_answer='Hash collisions are handled via separate chaining (linked list / balanced red-black tree in Java 8+) or open addressing.', key_points='Chaining, Open Addressing, Load Factor, O(1) average lookup'),
            InterviewQuestion(role_category='Software Engineer', question_type='Technical', skill_topic='System Design', question_text='What is the difference between Synchronous and Asynchronous execution in Web Applications?', sample_answer='Synchronous blocks thread until completion; Asynchronous uses event loop or workers to unblock IO.', key_points='Event Loop, Non-blocking I/O, Promises/Futures, Concurrency'),
            InterviewQuestion(role_category='Technology Analyst', question_type='Technical', skill_topic='DBMS', question_text='What are ACID properties in Relational Database Systems? Give a banking transfer example.', sample_answer='Atomicity, Consistency, Isolation, and Durability guarantee transaction reliability.', key_points='Atomicity all or nothing, Consistency valid state, Isolation concurrent isolation, Durability disk persistence'),
            InterviewQuestion(role_category='Software Engineer', question_type='HR', skill_topic='Behavioral', question_text='Tell me about a challenging technical project you built during your MCA at KIET.', sample_answer='Use the STAR method: Situation, Task, Action, Result highlighting technical depth and teamwork.', key_points='STAR method, Leadership, Architecture, Measurable Results'),
            InterviewQuestion(role_category='Cloud Developer', question_type='Technical', skill_topic='Cloud', question_text='How would you design a scalable URL shortener system like TinyURL?', sample_answer='Base62 encoding of 64-bit ID, distributed caching with Redis, and horizontally partitioned relational datastore.', key_points='Base62 hashing, Redis caching, Database Sharding, Rate Limiting')
        ]
        db.session.add_all(iqs)
        db.session.flush()

        print("7. Creating Study Plan & Capstone Project...")
        plan = StudyPlan(
            student_id=student_prof.id,
            title='KIET MCA Placement Master Sprint 2026-2028',
            target_company='TCS / Deloitte / Google',
            target_role='Software Engineer & Cloud Analyst',
            weekly_hours=15,
            start_date=date.today() - timedelta(days=6),
            target_date=date.today() + timedelta(days=24),
            ai_generated=True,
            status='Active'
        )
        db.session.add(plan)
        db.session.flush()

        db.session.add(StudyTask(plan_id=plan.id, student_id=student_prof.id, title='Advanced Graph Traversals (BFS & DFS)', skill_name='Data Structures and Algorithms', topic='Graphs', duration_minutes=60, priority='High', scheduled_date=date.today()-timedelta(days=2), is_completed=True, completed_at=datetime.utcnow()-timedelta(days=2)))
        db.session.add(StudyTask(plan_id=plan.id, student_id=student_prof.id, title='Database Normalization (BCNF, 3NF) & Indexing', skill_name='SQL', topic='Relational Theory', duration_minutes=45, priority='High', scheduled_date=date.today()-timedelta(days=1), is_completed=True, completed_at=datetime.utcnow()-timedelta(days=1)))
        db.session.add(StudyTask(plan_id=plan.id, student_id=student_prof.id, title='Full Stack RESTful API Development with Python & Flask', skill_name='Web Development', topic='REST APIs', duration_minutes=60, priority='High', scheduled_date=date.today(), is_completed=False))

        proj = StudentProject(
            student_id=student_prof.id,
            title='Student Pulse: AI Driven Career & Placement Hub',
            description='Unified web ecosystem connecting MCA scholars, faculty mentors, and placement cells with live analytics and skill gap diagnostics.',
            category='Academic Capstone',
            tech_stack='Python, Flask, SQLite, Bootstrap 5, Chart.js',
            github_url='https://github.com/2628mca0206-kiet/student-pulse',
            progress_percentage=85,
            status='In Progress'
        )
        db.session.add(proj)
        db.session.flush()
        db.session.add(ProjectMilestone(project_id=proj.id, title='Database Architecture & Relational Schema', is_completed=True, completed_at=datetime.utcnow()-timedelta(days=12)))
        db.session.add(ProjectMilestone(project_id=proj.id, title='Interactive 21-Games Skill Zone & Interview Engine', is_completed=True, completed_at=datetime.utcnow()-timedelta(days=1)))

        print("8. Creating 14-Day Activity Heatmap Logs & Streak...")
        today = date.today()
        for i in range(13, -1, -1):
            act_date = today - timedelta(days=i)
            db.session.add(StudentActivityLog(
                student_id=student_prof.id,
                activity_type='study_task',
                activity_title=f"MCA Preparation Session: Day {14-i}",
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

        # Faculty Feedback & Mentorship
        db.session.add(FacultyFeedback(
            faculty_id=faculty_prof.id,
            student_id=student_prof.id,
            feedback_text='Exceptional dedication in MCA Semester 1 exams. Consistently performing well in coding labs. Recommended to target Tier-1 product placement drives.',
            category='Placement',
            is_at_risk_alert=False
        ))
        db.session.add(MentorshipTarget(
            faculty_id=faculty_prof.id,
            student_id=student_prof.id,
            title='Master Tree and Graph Algorithms before Semester 3 Placement Drives',
            description='Solve 40 LeetCode Medium Problems and complete mock interview.',
            target_skill='Data Structures and Algorithms',
            deadline=date.today() + timedelta(days=30),
            status='In Progress'
        ))
        db.session.add(MentorshipSession(
            faculty_id=faculty_prof.id,
            student_id=student_prof.id,
            topic='MCA Placement Strategy & Tier-1 Company Preparation',
            scheduled_date=date.today() + timedelta(days=3),
            scheduled_time='4:00 PM',
            mode='Offline Cabin',
            notes='Review resume and capstone project architecture.'
        ))

        # Notifications
        db.session.add(Notification(
            user_id=student_user.id,
            title="Welcome to KIET Student Pulse!",
            message="Your official MCA placement profile (2628mca0206@kiet.edu) is verified and active.",
            category="info",
            link="/student/dashboard"
        ))
        db.session.add(Notification(
            user_id=student_user.id,
            title="TCS Campus Recruitment 2026-2028",
            message="Application submitted successfully. Status: Shortlisted for Technical Assessment.",
            category="success",
            link="/drives/"
        ))

        db.session.commit()
        print("-----------------------------------------------------------------")
        print("DATABASE INITIALIZED & SEEDED WITH OFFICIAL ACCOUNTS:")
        print("1. Student: 2628mca0206@kiet.edu  / Password: Student@123 (OTP 2-Step)")
        print("2. Staff:   staff@kiet.edu        / Password: Staff@123   (or Password@123)")
        print("3. Admin:   admin@kiet.edu        / Password: Admin@123   (or Password@123)")
        print("-----------------------------------------------------------------")

if __name__ == '__main__':
    seed_official_database()
