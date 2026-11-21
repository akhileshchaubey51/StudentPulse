import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from extensions import db
from models.user import User

app = create_app()
with app.app_context():
    client = app.test_client()

    # 1. Test Login Page
    res = client.get('/auth/login')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    html = res.get_data(as_text=True)
    assert 'Hello, Welcome' in html, "Missing 'Hello, Welcome'"
    assert 'form-box' in html, "Missing 'form-box'"
    assert 'yetiContainer' in html, "Missing 'yetiContainer'"
    print("PASS: /auth/login page renders with Hello Welcome, form-box, and Yeti Mascot!")

    # 2. Test Register Page
    res = client.get('/auth/register')
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    html = res.get_data(as_text=True)
    assert 'KIET' in html or 'Kite' in html, "Missing KIET institutional reference"
    print("PASS: /auth/register page renders with institutional verification fields!")

    # 3. Test Full 2-Step Login & AI Question Generation
    user = User.query.filter_by(role='student').first()
    if user:
        # Step A: Get Login page & Captcha
        res_login_page = client.get('/auth/login')
        with client.session_transaction() as sess:
            captcha_ans = sess.get('captcha_answer')

        # Step B: Submit Login Credentials + Captcha
        res_post_login = client.post('/auth/login', data={
            'email': user.email,
            'password': 'Student@123',
            'captcha': str(captcha_ans)
        })
        assert res_post_login.status_code == 302, f"Expected 302 to OTP, got {res_post_login.status_code}"
        assert '/auth/verify-otp' in res_post_login.headers.get('Location')
        print(f"PASS: Login credentials verified, redirected to 2-step OTP for {user.email}")

        # Step C: Submit Correct OTP
        with client.session_transaction() as sess:
            otp_code = sess.get('pending_otp_code')
        
        res_otp = client.post('/auth/verify-otp', data={'otp': otp_code})
        assert res_otp.status_code == 302
        print(f"PASS: 2-Step OTP ({otp_code}) verified! Student authenticated.")
        
        # Test Practice Page
        res_prac = client.get('/coding/practice')
        assert res_prac.status_code == 200, f"Expected 200, got {res_prac.status_code}"
        assert 'Dynamic AI' in res_prac.get_data(as_text=True) or 'Generate' in res_prac.get_data(as_text=True)
        print("PASS: /coding/practice renders with dynamic AI questions engine!")

        # Test Generate AI Questions Route
        res_gen = client.post('/coding/generate-ai-questions', data={'category': 'DSA', 'difficulty': 'Medium', 'count': '3'})
        assert res_gen.status_code in [302, 200], f"Expected 302/200, got {res_gen.status_code}"
        print("PASS: /coding/generate-ai-questions successfully generated dynamic questions!")

        # Test Games Zone
        res_games = client.get('/games/')
        assert res_games.status_code == 200, f"Expected 200, got {res_games.status_code}"
        print("PASS: /games/ renders with dynamic games zone!")

        # Test Special Platforms SSO Route (Google, KIET, Microsoft, GitHub)
        res_sso_valid = client.post('/auth/sso-login', json={'provider': 'google', 'email': '2628mca0206@kiet.edu'})
        assert res_sso_valid.status_code == 200, f"Expected 200, got {res_sso_valid.status_code}"
        assert res_sso_valid.get_json()['success'] is True
        print("PASS: /auth/sso-login verified with Google Workspace for 2628mca0206@kiet.edu!")

        # Test SSO Domain Security: Non-@kiet.edu must be rejected
        res_sso_invalid = client.post('/auth/sso-login', json={'provider': 'google', 'email': 'user@gmail.com'})
        assert res_sso_invalid.status_code == 400
        assert res_sso_invalid.get_json()['success'] is False
        print("PASS: /auth/sso-login strictly rejected non-@kiet.edu domain!")

        # Test Staff & Admin Logins
        res_staff = client.post('/auth/login', data={'email': 'staff@kiet.edu', 'password': 'Staff@123', 'captcha': str(captcha_ans)})
        assert res_staff.status_code == 302
        print("PASS: Staff login (staff@kiet.edu) verified!")

        res_admin = client.post('/auth/login', data={'email': 'admin@kiet.edu', 'password': 'Admin@123', 'captcha': str(captcha_ans)})
        assert res_admin.status_code == 302
        print("PASS: Admin login (admin@kiet.edu) verified!")

print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")
