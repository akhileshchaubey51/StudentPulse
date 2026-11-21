from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.notification import Notification

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/')
@login_required
def index():
    notifs = current_user.notifications.order_by(Notification.created_at.desc()).all()
    return render_template('notifications/index.html', notifications=notifs)


@notifications_bp.route('/mark-read/<int:notif_id>')
@login_required
def mark_read(notif_id):
    notif = Notification.query.filter_by(id=notif_id, user_id=current_user.id).first_or_404()
    notif.is_read = True
    db.session.commit()
    if notif.link:
        return redirect(notif.link)
    return redirect(url_for('notifications.index'))


@notifications_bp.route('/mark-all-read')
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    flash('All notifications marked as read.', 'info')
    return redirect(url_for('notifications.index'))
