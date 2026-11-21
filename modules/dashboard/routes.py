from flask import Blueprint, redirect, url_for
from flask_login import login_required, current_user

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if current_user.is_student():
        return redirect(url_for('student.dashboard'))
    elif current_user.is_faculty():
        return redirect(url_for('faculty.dashboard'))
    elif current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))
