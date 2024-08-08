from flask import Blueprint, request, jsonify
from ..models.user import User, db


auth_bp = Blueprint('auth_bp', __name__)

# Get all users
@auth_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    users_list = [user.serialize() for user in users]
    return jsonify(users_list)

# Get user by ID
@auth_bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.serialize())


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    is_admin = data.get('is_admin', False)  # Default to False if not provided
    worker_id = data.get('worker_id')
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': 'User already exists'}), 400
    user = User(username=username, email=email, is_admin=is_admin, worker_id=worker_id)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

@auth_bp.route('/users', methods=['DELETE'])
def delete_users():
    users = User.query.all()
    for user in users:
        db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "All users deleted successfully"}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    # Generate token or session here
    return jsonify({'message': 'Login successful'}), 200

@auth_bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    user.password_hash = data.get('password_hash', user.password_hash)
    user.is_admin = data.get('is_admin', user.is_admin)
    user.worker_id = data.get('worker_id', user.worker_id)
    db.session.commit()
    return jsonify(user.serialize())
