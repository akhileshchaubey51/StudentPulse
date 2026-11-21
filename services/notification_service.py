from extensions import db
from models.notification import Notification

def send_notification(user_id, title, message, category='info', link=None):
    """
    Creates and commits an in-app notification for a user.
    """
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        category=category,
        link=link,
        is_read=False
    )
    db.session.add(notif)
    db.session.commit()
    return notif
