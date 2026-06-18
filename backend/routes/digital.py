from flask import Blueprint, request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Book, ReadingProgress, Transaction, db
from datetime import datetime

digital_bp = Blueprint('digital', __name__)

@digital_bp.route('/<int:bid>/pdf', methods=['GET'])
@jwt_required()
def get_pdf(bid):
    uid = int(get_jwt_identity())
    book = Book.query.get_or_404(bid)
    if not book.is_digital:
        return jsonify({'error': 'Not a digital book'}), 400
    
    # Check access: admin/librarian or user has an active transaction
    has_access = False
    from models import User
    u = User.query.get(uid)
    if u.role in ['admin', 'librarian']:
        has_access = True
    else:
        if Transaction.query.filter_by(user_id=uid, book_id=bid, status='issued').first():
            has_access = True
            
    if not has_access:
        return jsonify({'error': 'You must borrow this book to read it online'}), 403
        
    if book.pdf_url:
        return redirect(book.pdf_url)
    return jsonify({'error': 'PDF URL not found'}), 404

@digital_bp.route('/<int:bid>/progress', methods=['GET'])
@jwt_required()
def get_progress(bid):
    uid = int(get_jwt_identity())
    p = ReadingProgress.query.filter_by(user_id=uid, book_id=bid).first()
    if p: return jsonify(p.to_dict())
    return jsonify({'current_page': 1, 'percent_complete': 0.0})

@digital_bp.route('/<int:bid>/progress', methods=['POST'])
@jwt_required()
def save_progress(bid):
    uid = int(get_jwt_identity())
    data = request.get_json()
    p = ReadingProgress.query.filter_by(user_id=uid, book_id=bid).first()
    if not p:
        p = ReadingProgress(user_id=uid, book_id=bid)
        db.session.add(p)
    p.current_page = data.get('current_page', p.current_page)
    p.total_pages = data.get('total_pages', p.total_pages)
    if p.total_pages and p.total_pages > 0:
        p.percent_complete = round((p.current_page / p.total_pages) * 100, 2)
        p.completed = p.current_page >= p.total_pages
    p.last_read_at = datetime.utcnow()
    db.session.commit()
    return jsonify(p.to_dict())

@digital_bp.route('/my-progress', methods=['GET'])
@jwt_required()
def my_progress():
    uid = int(get_jwt_identity())
    prog = ReadingProgress.query.filter_by(user_id=uid, completed=False).order_by(ReadingProgress.last_read_at.desc()).all()
    return jsonify([p.to_dict() for p in prog])
