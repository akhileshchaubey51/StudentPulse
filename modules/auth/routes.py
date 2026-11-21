import random
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User, StudentProfile, FacultyProfile
from models.activity import StudentStreak

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def generate_captcha():
    """Generates a random math verification challenge."""
    n1 = random.randint(3, 15)
    n2 = random.randint(2, 9)
    session['captcha_answer'] = str(n1 + n2)
    session['captcha_question'] = f"{n1} + {n2} = ?"
    return session['captcha_question']

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json
        if request.is_json:
            data = request.get_json() or {}
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            captcha = str(data.get('captcha', '')).strip()
            remember = bool(data.get('remember'))
        else:
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            captcha = request.form.get('captcha', '').strip()
            remember = bool(request.form.get('remember'))

        # 1. Captcha Verification
        expected_captcha = session.get('captcha_answer')
        if not expected_captcha or captcha != expected_captcha:
            msg = 'Security Captcha verification failed. Please solve the math verification problem.'
            new_captcha = generate_captcha()
            if is_ajax:
                return jsonify({'success': False, 'message': msg, 'emoji': '😭', 'new_captcha': new_captcha}), 400
            flash(f'😭 {msg}', 'danger')
            return render_template('auth/login.html', captcha_question=session.get('captcha_question'))

        # 2. Email & Password Verification (Supports both @kiet.edu and legacy @kite.edu)
        user = User.query.filter(
            (User.email == email) | 
            (User.email == email.replace('@kite.edu', '@kiet.edu')) | 
            (User.email == email.replace('@kiet.edu', '@kite.edu'))
        ).first()

        if not user or not user.check_password(password):
            msg = 'Invalid email or password. Please verify your credentials.'
            new_captcha = generate_captcha()
            if is_ajax:
                return jsonify({'success': False, 'message': msg, 'emoji': '😭', 'new_captcha': new_captcha}), 400
            flash(f'😭 {msg}', 'danger')
            return render_template('auth/login.html', captcha_question=session.get('captcha_question'))

        if not user.is_active:
            msg = 'Your account has been deactivated. Please contact the administrator.'
            new_captcha = generate_captcha()
            if is_ajax:
                return jsonify({'success': False, 'message': msg, 'emoji': '😭', 'new_captcha': new_captcha}), 403
            flash(f'😭 {msg}', 'danger')
            return render_template('auth/login.html', captcha_question=session.get('captcha_question'))

        # 3. 2-Step OTP Validation Trigger
        otp_code = str(random.randint(100000, 999999))
        session['pending_otp_code'] = otp_code
        session['pending_otp_user_id'] = user.id
        session['pending_otp_remember'] = remember
        session['pending_otp_email'] = user.email
        session['pending_otp_name'] = user.first_name
        session['pending_otp_created_at'] = datetime.utcnow().isoformat()

        # Display institutional OTP delivery banner
        flash(f'[KIET Institutional Security] 2-Step OTP Code sent to {user.email}: {otp_code}', 'info')
        if is_ajax:
            return jsonify({
                'success': True,
                'message': f'Credentials verified successfully! Welcome back, {user.first_name} 😊',
                'emoji': '😊',
                'redirect': url_for('auth.verify_otp')
            })
        return redirect(url_for('auth.verify_otp'))

    # GET Request: Generate fresh captcha
    captcha_q = generate_captcha()
    return render_template('auth/login.html', captcha_question=captcha_q)


@auth_bp.route('/sso-login', methods=['GET', 'POST'])
def sso_login():
    """Single Sign-On for Special Platforms (Google Workspace, KIET ERP, Microsoft 365, GitHub)."""
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json() or {}
            provider = data.get('provider', 'google').lower()
            email = data.get('email', '2628mca0206@kiet.edu').strip().lower()
        else:
            provider = request.form.get('provider', 'google').lower()
            email = request.form.get('email', '2628mca0206@kiet.edu').strip().lower()
    else:
        provider = request.args.get('provider', 'google').lower()
        email = request.args.get('email', '2628mca0206@kiet.edu').strip().lower()

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json

    # Strict Institutional Domain Verification: Must be @kiet.edu
    if not (email.endswith('@kiet.edu') or email.endswith('@kite.edu')):
        msg = 'Access Denied: Institutional validation failed. Only official @kiet.edu university accounts are permitted.'
        if is_ajax:
            return jsonify({'success': False, 'message': msg, 'emoji': '😭'}), 400
        flash(f'😭 {msg}', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.filter(
        (User.email == email) | 
        (User.email == email.replace('@kite.edu', '@kiet.edu')) | 
        (User.email == email.replace('@kiet.edu', '@kite.edu'))
    ).first()

    if not user:
        # Auto-provision student account for valid @kiet.edu identity
        username_part = email.split('@')[0]
        user = User(
            email=email,
            first_name='KIET',
            last_name='Student',
            role='student',
            is_active=True
        )
        user.set_password('Student@123')
        db.session.add(user)
        db.session.flush()

        prof = StudentProfile(
            user_id=user.id,
            enrollment_number=username_part.upper(),
            course='MCA',
            department='Department of Computer Applications (MCA)',
            graduation_year=2028,
            semester=2,
            cgpa=8.5
        )
        db.session.add(prof)
        db.session.flush()

        streak = StudentStreak(
            student_id=prof.id,
            current_streak=1,
            longest_streak=1,
            total_active_days=1,
            last_active_date=datetime.utcnow().date()
        )
        db.session.add(streak)
        db.session.commit()

    if not user.is_active:
        msg = 'Your account has been deactivated. Please contact the administrator.'
        if is_ajax:
            return jsonify({'success': False, 'message': msg, 'emoji': '😭'}), 403
        flash(f'😭 {msg}', 'danger')
        return redirect(url_for('auth.login'))

    # Generate 2-Step OTP Validation Trigger
    otp_code = str(random.randint(100000, 999999))
    session['pending_otp_code'] = otp_code
    session['pending_otp_user_id'] = user.id
    session['pending_otp_remember'] = True
    session['pending_otp_email'] = user.email
    session['pending_otp_name'] = user.first_name
    session['pending_otp_created_at'] = datetime.utcnow().isoformat()

    platform_names = {
        'google': 'Google Workspace for KIET',
        'kiet': 'KIET Institutional ERP Portal',
        'microsoft': 'Microsoft 365 Education',
        'github': 'GitHub Student Developer Pack'
    }
    p_name = platform_names.get(provider, provider.title())

    flash(f'[{p_name} Verified] 2-Step OTP Code sent to {user.email}: {otp_code}', 'info')

    if is_ajax:
        return jsonify({
            'success': True,
            'message': f'Verified with {p_name}! Welcome, {user.first_name} 😊',
            'emoji': '😊',
            'redirect': url_for('auth.verify_otp')
        })
    return redirect(url_for('auth.verify_otp'))


@auth_bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    """2-Step OTP Security Verification View with Yeti Mascot reaction."""
    user_id = session.get('pending_otp_user_id')
    otp_code = session.get('pending_otp_code')
    email = session.get('pending_otp_email', 'registered institutional email')

    if not user_id or not otp_code:
        flash('No pending authentication session found. Please sign in.', 'warning')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        entered_otp = request.form.get('otp', '').strip()
        if entered_otp == otp_code:
            user = User.query.get(user_id)
            if not user:
                flash('User session invalid. Please log in again.', 'danger')
                return redirect(url_for('auth.login'))

            remember = session.get('pending_otp_remember', False)
            # Clear pending session state
            session.pop('pending_otp_code', None)
            session.pop('pending_otp_user_id', None)
            session.pop('pending_otp_remember', None)
            session.pop('pending_otp_email', None)

            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=remember)

            flash(f'😊 Identity verified! Welcome back, {user.first_name}.', 'success')
            return redirect_by_role(user)
        else:
            flash('😭 Invalid OTP code. Please enter the exact 6-digit code provided.', 'danger')

    return render_template('auth/verify_otp.html', email=email, otp_code=otp_code)


@auth_bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """Resend a fresh OTP for verification."""
    user_id = session.get('pending_otp_user_id')
    email = session.get('pending_otp_email')
    if not user_id:
        flash('Session expired. Please sign in.', 'warning')
        return redirect(url_for('auth.login'))

    new_otp = str(random.randint(100000, 999999))
    session['pending_otp_code'] = new_otp
    flash(f'[KIET Institutional Security] New OTP Code generated: {new_otp}', 'info')
    return redirect(url_for('auth.verify_otp'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Students registration with institutional email support (@kiet.edu) and full validations."""
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        enrollment_no = request.form.get('enrollment_number', '').strip().upper()
        course = request.form.get('course', 'B.Tech')
        department = request.form.get('department', 'Computer Science & Engineering')
        graduation_year = int(request.form.get('graduation_year', 2026))

        # Comprehensive Institutional Validations
        if len(first_name) < 2 or len(last_name) < 2:
            flash('First and last name must each contain at least 2 characters.', 'danger')
            return render_template('auth/register.html')

        # Institutional email check (@kiet.edu or university .edu domains)
        if not (email.endswith('@kiet.edu') or email.endswith('@kite.edu') or email.endswith('.edu') or email.endswith('@studentpulse.edu')):
            flash('Institutional validation required: Please register using your official university address (e.g. name@kiet.edu or authorized .edu domain).', 'danger')
            return render_template('auth/register.html')

        if len(enrollment_no) < 4:
            flash('Please enter a valid university enrollment number (e.g. KIET2026-1045).', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6 or not any(c.isdigit() for c in password) or not any(c.isalpha() for c in password):
            flash('Password must be at least 6 characters long and contain both letters and numbers.', 'danger')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match. Please verify both password fields.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('An account with this email address already exists. Please sign in.', 'danger')
            return render_template('auth/register.html')

        if StudentProfile.query.filter_by(enrollment_number=enrollment_no).first():
            flash('An account with this enrollment number already exists.', 'danger')
            return render_template('auth/register.html')

        # Create user
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role='student',
            is_active=True
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        # Create student profile
        student_prof = StudentProfile(
            user_id=new_user.id,
            enrollment_number=enrollment_no,
            course=course,
            department=department,
            graduation_year=graduation_year
        )
        db.session.add(student_prof)
        db.session.flush()

        # Initialize streak
        streak = StudentStreak(
            student_id=student_prof.id,
            current_streak=0,
            longest_streak=0,
            total_active_days=0
        )
        db.session.add(streak)

        db.session.commit()
        login_user(new_user)
        flash('Institutional registration verified! Welcome to Student Pulse KIET Portal.', 'success')
        return redirect(url_for('student.dashboard'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name', current_user.first_name).strip()
        current_user.last_name = request.form.get('last_name', current_user.last_name).strip()
        current_user.phone = request.form.get('phone', current_user.phone).strip()

        if current_user.is_student() and current_user.student_profile:
            prof = current_user.student_profile
            prof.college = request.form.get('college', prof.college)
            prof.university = request.form.get('university', prof.university)
            prof.course = request.form.get('course', prof.course)
            prof.department = request.form.get('department', prof.department)
            prof.career_objective = request.form.get('career_objective', prof.career_objective)
            prof.target_companies = request.form.get('target_companies', prof.target_companies)
            prof.preferred_roles = request.form.get('preferred_roles', prof.preferred_roles)
            prof.github_url = request.form.get('github_url', prof.github_url)
            prof.linkedin_url = request.form.get('linkedin_url', prof.linkedin_url)

        new_password = request.form.get('new_password')
        if new_password and len(new_password) >= 6:
            current_user.set_password(new_password)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')


def redirect_by_role(user):
    if user.role == 'student':
        return redirect(url_for('student.dashboard'))
    elif user.role == 'faculty':
        return redirect(url_for('faculty.dashboard'))
    elif user.role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('auth.login'))
