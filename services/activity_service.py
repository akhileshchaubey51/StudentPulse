from datetime import date, datetime, timedelta
from extensions import db
from models.activity import StudentActivityLog, StudentStreak
from services.streak_service import update_student_streak

def log_activity(student_id, activity_type, activity_title, duration_minutes=30, related_record_id=None, activity_date=None):
    """
    Records a genuine completed learning activity for a student.
    Qualifying types: 'study_task', 'coding_quiz', 'skill_assessment', 'project_milestone', 'interview_mock', 'learning_session'.
    Automatically triggers streak calculation.
    """
    if activity_date is None:
        activity_date = date.today()

    log = StudentActivityLog(
        student_id=student_id,
        activity_type=activity_type,
        activity_title=activity_title,
        duration_minutes=duration_minutes,
        related_record_id=related_record_id,
        activity_date=activity_date,
        status='completed',
        created_at=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()

    # Update streak
    update_student_streak(student_id)
    return log


def get_heatmap_data(student_id, year=None):
    """
    Generates a full 365-day LeetCode/GitHub contribution heatmap dataset.
    Returns:
    - grid: list of 52-53 week columns, each with 7 day objects {date_str, count, minutes, level, color}
    - summary: total active days, current streak, longest streak, total activities, total hours
    - month_labels: positions for month headers
    """
    today = date.today()
    if year is None:
        year = today.year

    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)

    # Fetch all activity records for this student and year
    logs = StudentActivityLog.query.filter(
        StudentActivityLog.student_id == student_id,
        StudentActivityLog.activity_date >= start_date,
        StudentActivityLog.activity_date <= end_date,
        StudentActivityLog.status == 'completed'
    ).all()

    # Aggregate by date
    daily_stats = {}
    total_minutes = 0
    total_activities = len(logs)

    for log in logs:
        d_str = log.activity_date.isoformat()
        if d_str not in daily_stats:
            daily_stats[d_str] = {'count': 0, 'minutes': 0, 'types': set(), 'items': []}
        daily_stats[d_str]['count'] += 1
        daily_stats[d_str]['minutes'] += (log.duration_minutes or 0)
        daily_stats[d_str]['types'].add(log.activity_type)
        daily_stats[d_str]['items'].append(log.activity_title)
        total_minutes += (log.duration_minutes or 0)

    # Determine start grid day (adjusting so Sunday=0 or Monday=0)
    # Python weekday(): Monday is 0 and Sunday is 6.
    # Standard contribution calendar has Sunday as row 0.
    # Let's align Sunday to index 0:
    # (day.weekday() + 1) % 7 gives Sunday=0, Monday=1, ..., Saturday=6.
    current_day = start_date
    first_col_padding = (current_day.weekday() + 1) % 7

    weeks = []
    current_week = []

    # Pad first week before Jan 1
    for i in range(first_col_padding):
        pad_date = start_date - timedelta(days=first_col_padding - i)
        current_week.append({
            'date': pad_date.isoformat(),
            'in_year': False,
            'count': 0,
            'minutes': 0,
            'level': 0,
            'color': '#F1F3F4'
        })

    month_labels = []
    last_month = None

    while current_day <= end_date:
        if current_day.month != last_month:
            month_labels.append({
                'month_name': current_day.strftime('%b'),
                'week_index': len(weeks)
            })
            last_month = current_day.month

        d_str = current_day.isoformat()
        stat = daily_stats.get(d_str, {'count': 0, 'minutes': 0, 'types': set(), 'items': []})
        cnt = stat['count']
        mins = stat['minutes']

        # Determine level & color based on LeetCode/GitHub specification:
        # 0: #F1F3F4 (No activity)
        # 1: #DDF5E5 (1 activity)
        # 2: #A8DFAF (2 activities)
        # 3: #59C77C (3-4 activities)
        # 4: #218C4A (5+ activities)
        if cnt == 0:
            level = 0
            color = '#F1F3F4'
        elif cnt == 1:
            level = 1
            color = '#DDF5E5'
        elif cnt == 2:
            level = 2
            color = '#A8DFAF'
        elif cnt <= 4:
            level = 3
            color = '#59C77C'
        else:
            level = 4
            color = '#218C4A'

        current_week.append({
            'date': d_str,
            'formatted_date': current_day.strftime('%a, %b %d, %Y'),
            'in_year': True,
            'count': cnt,
            'minutes': mins,
            'level': level,
            'color': color,
            'items': stat['items'][:5]
        })

        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []

        current_day += timedelta(days=1)

    # Pad the remaining days of the last week
    if current_week:
        while len(current_week) < 7:
            current_week.append({
                'date': '',
                'in_year': False,
                'count': 0,
                'minutes': 0,
                'level': 0,
                'color': '#F1F3F4'
            })
        weeks.append(current_week)

    # Streak record
    streak = StudentStreak.query.filter_by(student_id=student_id).first()

    return {
        'year': year,
        'weeks': weeks,
        'month_labels': month_labels,
        'total_active_days': len(daily_stats),
        'total_activities': total_activities,
        'total_hours': round(total_minutes / 60.0, 1),
        'current_streak': streak.current_streak if streak else 0,
        'longest_streak': streak.longest_streak if streak else 0
    }
