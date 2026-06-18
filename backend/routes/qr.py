import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
import qrcode
from models import User, Book, db

qr_bp = Blueprint('qr', __name__)

QR_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'qr')
os.makedirs(QR_DIR, exist_ok=True)

def generate_qr_image(data, filename):
    img = qrcode.make(data)
    filepath = os.path.join(QR_DIR, filename)
    img.save(filepath)
    return f'/api/qr/image/{filename}'

@qr_bp.route('/image/<filename>')
def serve_qr(filename):
    return send_from_directory(QR_DIR, filename)

@qr_bp.route('/generate/book/<int:bid>', methods=['POST'])
@jwt_required()
def generate_book_qr(bid):
    user = User.query.get(int(get_jwt_identity()))
    if user.role not in ['admin', 'librarian']: return jsonify({'error': 'Unauthorized'}), 403
    book = Book.query.get_or_404(bid)
    code = f'KUL-BOOK-{bid}'
    filename = f'book_{bid}.png'
    path = generate_qr_image(code, filename)
    book.qr_code = path
    db.session.commit()
    return jsonify({'message': 'QR code generated', 'path': path})

@qr_bp.route('/generate/user/<int:uid>', methods=['POST'])
@jwt_required()
def generate_user_qr(uid):
    user = User.query.get(int(get_jwt_identity()))
    if user.role not in ['admin', 'librarian']: return jsonify({'error': 'Unauthorized'}), 403
    target_user = User.query.get_or_404(uid)
    code = f'KUL-USER-{uid}'
    filename = f'user_{uid}.png'
    path = generate_qr_image(code, filename)
    target_user.qr_code = path
    db.session.commit()
    return jsonify({'message': 'QR code generated', 'path': path})

@qr_bp.route('/scan', methods=['POST'])
@jwt_required()
def scan_qr():
    user = User.query.get(int(get_jwt_identity()))
    if user.role not in ['admin', 'librarian']: return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    code = data.get('code', '')
    if code.startswith('KUL-BOOK-'):
        bid = int(code.split('-')[-1])
        book = Book.query.get(bid)
        if book:
            return jsonify({'type': 'book', 'id': book.id, 'title': book.title, 'available': book.available_copies > 0, 'cover': book.cover_image})
    elif code.startswith('KUL-USER-'):
        uid = int(code.split('-')[-1])
        u = User.query.get(uid)
        if u:
            active_loans = len([t for t in u.transactions if t.status == 'issued'])
            return jsonify({'type': 'user', 'id': u.id, 'name': u.full_name or u.username, 'active_loans': active_loans})
    return jsonify({'error': 'Invalid or unknown QR code'}), 404

@qr_bp.route('/issue', methods=['POST'])
@jwt_required()
def issue_qr():
    user = User.query.get(int(get_jwt_identity()))
    if user.role not in ['admin', 'librarian']: return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    from routes.transactions import issue_book_helper
    try:
        user_id = int(data['user_code'].split('-')[-1])
        book_id = int(data['book_code'].split('-')[-1])
        res, status = issue_book_helper(user_id, book_id, user.id)
        return jsonify(res), status
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@qr_bp.route('/return', methods=['POST'])
@jwt_required()
def return_qr():
    user = User.query.get(int(get_jwt_identity()))
    if user.role not in ['admin', 'librarian']: return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    from routes.transactions import return_book_helper
    try:
        user_id = int(data['user_code'].split('-')[-1])
        book_id = int(data['book_code'].split('-')[-1])
        res, status = return_book_helper(user_id, book_id, user.id)
        return jsonify(res), status
    except Exception as e:
        return jsonify({'error': str(e)}), 400
