from extensions import db
from models.user import User, StudentProfile, FacultyProfile, AdminProfile
from models.academic import Department, Course, Semester, Batch, Section, StudentBatchAssignment, FacultyBatchAssignment, FacultyStudentAssignment
from models.skill import Skill, StudentSkill, SkillAssessment, SkillAssessmentResult
from models.company import Company, JobRole, JobRoleSkill
from models.campus_drive import CampusDrive, DriveApplication
from models.study_plan import StudyPlan, StudyTask
from models.project import StudentProject, ProjectMilestone, ProjectReview
from models.assessment import Question, Assessment, AssessmentQuestion, AssessmentAttempt, AssessmentAnswer
from models.interview import InterviewQuestion, MockInterview, InterviewResponse
from models.resume import Resume
from models.faculty import FacultyFeedback, MentorshipTarget, MentorshipSession
from models.activity import StudentActivityLog, StudentStreak
from models.notification import Notification

__all__ = [
    'User', 'StudentProfile', 'FacultyProfile', 'AdminProfile',
    'Department', 'Course', 'Semester', 'Batch', 'Section',
    'StudentBatchAssignment', 'FacultyBatchAssignment', 'FacultyStudentAssignment',
    'Skill', 'StudentSkill', 'SkillAssessment', 'SkillAssessmentResult',
    'Company', 'JobRole', 'JobRoleSkill',
    'CampusDrive', 'DriveApplication',
    'StudyPlan', 'StudyTask',
    'StudentProject', 'ProjectMilestone', 'ProjectReview',
    'Question', 'Assessment', 'AssessmentQuestion', 'AssessmentAttempt', 'AssessmentAnswer',
    'InterviewQuestion', 'MockInterview', 'InterviewResponse',
    'Resume',
    'FacultyFeedback', 'MentorshipTarget', 'MentorshipSession',
    'StudentActivityLog', 'StudentStreak',
    'Notification'
]
