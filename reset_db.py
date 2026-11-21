"""
Student Pulse - Clean Data / Database Reset Utility
Use this script to wipe demo data or reset to a fresh baseline.
"""
from app import create_app
from extensions import db
from models.activity import StudentActivityLog, StudentStreak
from models.assessment import AssessmentAttempt, AssessmentAnswer
from models.interview import MockInterview, InterviewResponse
from models.study_plan import StudyPlan, StudyTask
from models.project import StudentProject, ProjectMilestone, ProjectReview
from models.faculty import FacultyFeedback, MentorshipTarget

def clear_demo_data():
    app = create_app()
    with app.app_context():
        print("Clearing demo activity, streaks, quiz attempts, and mock interview logs...")
        
        # 1. Clear activity logs & reset streaks
        StudentActivityLog.query.delete()
        for s in StudentStreak.query.all():
            s.current_streak = 0
            s.longest_streak = 0
            s.total_active_days = 0
            s.last_active_date = None
            
        # 2. Clear quiz attempts
        AssessmentAnswer.query.delete()
        AssessmentAttempt.query.delete()

        # 3. Clear mock interviews
        InterviewResponse.query.delete()
        MockInterview.query.delete()

        # 4. Clear faculty feedbacks
        FacultyFeedback.query.delete()
        MentorshipTarget.query.delete()

        db.session.commit()
        print("Successfully wiped all demo activity records!")
        print("User accounts, verified companies, questions, and skills are preserved.")
        print("The platform is now in a clean, fresh state.")

if __name__ == '__main__':
    clear_demo_data()
