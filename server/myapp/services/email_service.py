from flask_mail import Mail, Message
from flask import current_app
from itsdangerous import URLSafeTimedSerializer


mail = Mail()

def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt='email-confirmation-salt')

def verify_token(token, expiration=3600):  # 1 hour expiration
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-confirmation-salt', max_age=expiration)
    except Exception:
        return None
    return email

def send_verification_email(user_email):
    token = generate_token(user_email)
    verify_url = f"{current_app.config['FRONTEND_URL']}/verify/{token}"  
    msg = Message(
        subject="Confirm Your Email",
        recipients=[user_email],
        body=f"Please confirm your email by clicking the following link: {verify_url}"
    )
    mail.send(msg)

def send_test_email(user_email):
    try:
        msg = Message(
            subject="Test Email",
            recipients=[user_email],
            body="This is a test email to check if email sending works."
        )
        mail.send(msg)
        current_app.logger.info(f"Test email sent to {user_email}")
    except Exception as e:
        current_app.logger.error(f"Failed to send test email to {user_email}: {e}")
        raise e

def send_password_reset_email(user_email):
    token = generate_token(user_email)
    reset_url = f"{current_app.config['FRONTEND_URL']}/reset-password/{token}"
    msg = Message(
        subject="Password Reset Request",
        recipients=[user_email],
        body=f"To reset your password, click the following link: {reset_url}. If you did not request a password reset, please ignore this email."
    )
    mail.send(msg)
