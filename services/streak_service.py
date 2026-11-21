from datetime import date, timedelta, datetime
from extensions import db
from models.activity import StudentActivityLog, StudentStreak

def update_student_streak(student_id):
    """
    Recalculates a student's current streak, longest streak, and total active days
    from genuine database activity records.
    Streak Rules:
    - A qualifying completed learning activity counts as an active day.
    - Multiple activities on one date count as one active day.
    - Consecutive active days increase the current streak.
    - If today has activity, streak continues.
    - If today has no activity yet, but yesterday had activity, streak is preserved (current_streak still alive).
    - If inactive for >= 2 days, current streak resets to 0.
    - Longest streak is preserved permanently.
    """
    streak_record = StudentStreak.query.filter_by(student_id=student_id).first()
    if not streak_record:
        streak_record = StudentStreak(
            student_id=student_id,
            current_streak=0,
            longest_streak=0,
            total_active_days=0
        )
        db.session.add(streak_record)

    # Get distinct active dates ordered descending
    active_dates_query = db.session.query(StudentActivityLog.activity_date)\
        .filter(StudentActivityLog.student_id == student_id, StudentActivityLog.status == 'completed')\
        .distinct()\
        .order_by(StudentActivityLog.activity_date.desc())\
        .all()

    active_dates = [d[0] for d in active_dates_query]
    total_active_days = len(active_dates)

    if not active_dates:
        streak_record.current_streak = 0
        streak_record.total_active_days = 0
        streak_record.last_active_date = None
        streak_record.updated_at = datetime.utcnow()
        db.session.commit()
        return streak_record

    latest_date = active_dates[0]
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Check if streak is still active
    # Active if latest activity is today or yesterday
    is_streak_active = (latest_date == today) or (latest_date == yesterday)

    current_streak = 0
    if is_streak_active:
        # Count consecutive days backwards starting from latest_date
        current_streak = 1
        expected_date = latest_date - timedelta(days=1)
        for d in active_dates[1:]:
            if d == expected_date:
                current_streak += 1
                expected_date = d - timedelta(days=1)
            elif d < expected_date:
                break
    else:
        current_streak = 0

    # Calculate longest historical streak
    # Sort dates ascending
    sorted_dates = sorted(active_dates)
    longest_streak = 0
    temp_streak = 0
    prev_d = None

    for d in sorted_dates:
        if prev_d is None:
            temp_streak = 1
        elif d == prev_d + timedelta(days=1):
            temp_streak += 1
        else:
            temp_streak = 1
        prev_d = d
        if temp_streak > longest_streak:
            longest_streak = temp_streak

    # Also make sure longest_streak is at least current_streak or existing longest_streak
    if current_streak > longest_streak:
        longest_streak = current_streak
    if streak_record.longest_streak and streak_record.longest_streak > longest_streak:
        longest_streak = streak_record.longest_streak

    streak_record.current_streak = current_streak
    streak_record.longest_streak = longest_streak
    streak_record.total_active_days = total_active_days
    streak_record.last_active_date = latest_date
    streak_record.updated_at = datetime.utcnow()

    db.session.commit()
    return streak_record
