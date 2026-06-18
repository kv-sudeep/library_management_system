from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User, AuditLog, Notification
from extensions import db
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data.get('email')).first():
        return jsonify({'error':'Email already exists'}), 400
    if User.query.filter_by(username=data.get('username')).first():
        return jsonify({'error':'Username already exists'}), 400
    user = User(username=data['username'], email=data['email'],
                full_name=data.get('full_name',''), phone=data.get('phone',''), role='member')
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    n = Notification(user_id=user.id, title='Welcome!',
        message=f'Welcome to LibraryOS, {user.full_name or user.username}!', type='welcome')
    db.session.add(n)
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return jsonify({'token':token,'user':user.to_dict()}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not user.check_password(data.get('password','')):
        return jsonify({'error':'Invalid credentials'}), 401
    if not user.is_active:
        return jsonify({'error':'Account deactivated'}), 403
    log = AuditLog(user_id=user.id, action='LOGIN', resource='auth', ip_address=request.remote_addr)
    db.session.add(log)
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return jsonify({'token':token,'user':user.to_dict()})

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user = User.query.get(int(get_jwt_identity()))
    return jsonify(user.to_dict()) if user else (jsonify({'error':'Not found'}), 404)

@auth_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    user = User.query.get(int(get_jwt_identity()))
    data = request.get_json()
    for f in ['full_name','phone','address']:
        if f in data: setattr(user, f, data[f])
    db.session.commit()
    return jsonify(user.to_dict())
