from flask import request, url_for, current_app, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from ..models.user import User, db
from ..services.email_service import send_verification_email, send_password_reset_email, verify_token, send_test_email
from http import HTTPStatus

api = Namespace('auth', description='Authentication operations')

# Constants for admin user validation
ADMIN_EMAIL_DOMAIN = 'ireporter.com'
VALID_WORKER_IDS = ['IRA1', 'IRA2', 'IRA3', 'IRA4', 'IRA5']

# Models for API documentation and data validation
user_model = api.model('User', {
    'id': fields.Integer(readonly=True, description='The user ID'),
    'email': fields.String(description='The user email address'),
    'is_admin': fields.Boolean(readonly=True, description='Admin status'),
    'worker_id': fields.String(description='Worker ID for admin users'),
    'created_at': fields.DateTime(readonly=True, description='The user creation timestamp'),
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='The user email address'),
    'password': fields.String(required=True, description='The user password')
})

user_register_model = api.model('UserRegister', {
    'email': fields.String(required=True, description='The user email address'),
    'password': fields.String(required=True, description='The user password'),
    'worker_id': fields.String(description='Worker ID for admin users')
})

# Helper function for password validation
def validate_password(password):
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char in "!@#$%^&*()_+-=[]{}|;':,.<>?/~`" for char in password):
        return False
    return True


@api.route('/register')
class Register(Resource):
    def post(self):
        data = request.get_json()

        if not data:
            return {'message': 'No input data provided'}, int(HTTPStatus.BAD_REQUEST)

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'message': 'Email and password are required'}, int(HTTPStatus.BAD_REQUEST)

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {'message': 'User already exists'}, int(HTTPStatus.CONFLICT)

        # Create new user and set the password
        new_user = User(email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        # Send verification email
        try:
            send_verification_email(email)
            # send_test_email(email)
        except Exception as e:
            db.session.delete(new_user)
            db.session.commit()
            current_app.logger.error(f"Failed to send verification email to {email}: {e}")
            return {'message': 'Failed to send verification email, please try again later.'}, int(HTTPStatus.INTERNAL_SERVER_ERROR)

        return {'message': 'User registered successfully. Please check your email to verify your account.'}, int(HTTPStatus.CREATED)


@api.route('/verify/<token>')
class EmailVerification(Resource):
    def get(self, token):
        email = verify_token(token)
        if not email:
            return {'message': 'Invalid or expired token'}, 400

        user = User.query.filter_by(email=email).first()
        if not user:
            return {'message': 'User not found'}, 404
        if user.is_verified:
            return {'message': 'User already verified'}, 200

        user.is_verified = True
        db.session.commit()
        return {'message': 'Email verified successfully'}, 200


@api.route('/forgot-password')
class ForgotPassword(Resource):
    def post(self):
        email = request.json.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            send_password_reset_email(email)
        return {'message': 'If the email is valid, a password reset link has been sent.'}, 200

@api.route('/reset-password/<token>')
class ResetPassword(Resource):
    def post(self, token):
        email = verify_token(token)
        if not email:
            return {'message': 'Invalid or expired token'}, 400

        data = request.get_json()
        new_password = data.get('password')
        if not new_password:
            return {'message': 'Password is required'}, 400

        user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            return {'message': 'Password has been reset successfully'}, 200

        return {'message': 'User not found'}, 404



@api.route('/login')
class UserLogin(Resource):
    @api.expect(login_model)
    @api.doc(responses={200: 'Login successful', 401: 'Invalid credentials'})
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.public_id)
            refresh_token = create_refresh_token(identity=user.public_id)
            user_data = user.to_dict()
            return {
                'message': 'Logged in successfully',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user_data
            }, 200
        return {'message': 'Invalid email or password'}, 401


@api.route('/refresh')
class UserRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        current_user_public_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_public_id)
        return {'access_token': new_access_token}, 200

@api.route('/user')
class UserProfile(Resource):
    @jwt_required()
    @api.marshal_with(user_model)
    def get(self):
        try:
            current_user_public_id = get_jwt_identity()
            user = User.query.filter_by(public_id=current_user_public_id).first()
            if not user:
                return {'error': 'User not found'}, 404
            return user.to_dict(), 200
        except Exception:
            return {'error': 'Internal Server Error'}, 500

@api.route('/users/<int:id>')
@api.param('id', 'The user identifier')
class UserUpdate(Resource):
    @jwt_required()
    @api.expect(user_model)
    @api.marshal_with(user_model)
    def put(self, id):
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        if not user or user.id != id:
            return {'error': 'Unauthorized'}, 403
        data = request.json
        user.email = data.get('email', user.email)
        if 'password' in data:
            user.password = generate_password_hash(data['password'])
        db.session.commit()
        return user

    @jwt_required()
    def delete(self, id):
        current_user_public_id = get_jwt_identity()
        user = User.query.filter_by(public_id=current_user_public_id).first()
        if not user or (not user.is_admin and user.id != id):
            return {'error': 'Unauthorized'}, 403
        user_to_delete = User.query.get(id)
        if not user_to_delete:
            return {'error': 'User not found'}, 404
        db.session.delete(user_to_delete)
        db.session.commit()
        return {'message': 'User deleted successfully'}, 200

@api.route('/logout')
class UserLogout(Resource):
    @jwt_required()
    def post(self):
        return {'message': 'Successfully logged out'}, 200

@api.route('/delete-user/<int:user_id>')
@api.param('user_id', 'The user identifier')
class DeleteUser(Resource):
    @jwt_required()
    def delete(self, user_id):
        current_user_public_id = get_jwt_identity()
        current_user = User.query.filter_by(public_id=current_user_public_id).first()

        if not current_user:
            return {'message': 'User not found'}, 404

        user_to_delete = User.query.get(user_id)
        
        if not user_to_delete:
            return {'message': 'User not found'}, 404

        # Check if the current user is trying to delete their own account
        # or if they are an admin
        if user_to_delete.id != current_user.id and not current_user.is_admin:
            return {'message': 'Unauthorized action'}, 403

        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            return {'message': 'User deleted successfully'}, 200
        except SQLAlchemyError as e:
            current_app.logger.error(f"Error deleting user: {e}")
            return {'message': 'Failed to delete user, please try again later.'}, 500
        
