from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, AuditLog
from extensions import db

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    uid = int(get_jwt_identity()); user = User.query.get(uid)
    if user.role not in ['admin','librarian']: return jsonify({'error':'Unauthorized'}),403
    page = request.args.get('page',1,type=int)
    search = request.args.get('search',''); role = request.args.get('role','')
    q = User.query
    if search: q = q.filter(db.or_(User.username.ilike(f'%{search}%'),User.email.ilike(f'%{search}%'),User.full_name.ilike(f'%{search}%')))
    if role: q = q.filter_by(role=role)
    p = q.paginate(page=page,per_page=50,error_out=False)
    return jsonify({'users':[u.to_dict() for u in p.items],'total':p.total})

@users_bp.route('/<int:uid>', methods=['GET'])
@jwt_required()
def get_user(uid):
    me = int(get_jwt_identity()); req = User.query.get(me)
    if req.role not in ['admin','librarian'] and me!=uid: return jsonify({'error':'Unauthorized'}),403
    return jsonify(User.query.get_or_404(uid).to_dict())

@users_bp.route('/<int:uid>', methods=['PUT'])
@jwt_required()
def update_user(uid):
    me = int(get_jwt_identity()); req = User.query.get(me)
    if req.role not in ['admin'] and me!=uid: return jsonify({'error':'Unauthorized'}),403
    user = User.query.get_or_404(uid); data = request.get_json()
    for f in ['full_name','phone','address','is_active']:
        if f in data: setattr(user,f,data[f])
    if 'role' in data and req.role=='admin': user.role=data['role']
    db.session.commit()
    return jsonify(user.to_dict())

@users_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
def audit_logs():
    uid = int(get_jwt_identity()); user = User.query.get(uid)
    if user.role!='admin': return jsonify({'error':'Unauthorized'}),403
    page = request.args.get('page',1,type=int)
    p = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page,per_page=50,error_out=False)
    return jsonify({'logs':[l.to_dict() for l in p.items],'total':p.total})
