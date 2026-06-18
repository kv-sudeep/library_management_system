from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Transaction, Book, User, Reservation, Notification, AuditLog
from extensions import db
from datetime import datetime, timedelta

transactions_bp = Blueprint('transactions', __name__)
FINE_PER_DAY = 2.0

def issue_book_helper(uid, book_id, req_id, loan_days=14):
    book = Book.query.get(book_id)
    if not book: return {'error':'Book not found'}, 404
    if book.available_copies <= 0: return {'error':'No copies available'}, 400
    if Transaction.query.filter_by(user_id=uid,status='issued').count() >= 5:
        return {'error':'Max 5 books at a time'}, 400
    due = datetime.utcnow() + timedelta(days=loan_days)
    t = Transaction(user_id=uid,book_id=book.id,due_date=due,status='issued',issued_by=req_id)
    book.available_copies -= 1
    res = Reservation.query.filter_by(user_id=uid,book_id=book.id,status='pending').first()
    if res: res.status='fulfilled'
    db.session.add(t)
    db.session.add(Notification(user_id=uid,title='Book Issued',
        message=f'"{book.title}" issued. Due: {due.strftime("%Y-%m-%d")}',type='issue'))
    db.session.add(AuditLog(user_id=req_id,action='ISSUE_BOOK',resource='transaction',
        details=f'Book {book.id} to User {uid}'))
    db.session.commit()
    return t.to_dict(), 201

def execute_return(t, req_id):
    now = datetime.utcnow()
    t.return_date = now; t.status = 'returned'
    if now > t.due_date:
        t.fine_amount = (now - t.due_date).days * FINE_PER_DAY
    t.book.available_copies += 1
    db.session.add(Notification(user_id=t.user_id,title='Book Returned',
        message=f'"{t.book.title}" returned. Fine: ${t.fine_amount:.2f}',type='return'))
    db.session.add(AuditLog(user_id=req_id,action='RETURN_BOOK',resource='transaction',details=f'Book {t.book_id} from User {t.user_id}'))
    db.session.commit()
    return t.to_dict(), 200

def return_book_helper(uid, book_id, req_id):
    t = Transaction.query.filter_by(user_id=uid, book_id=book_id, status='issued').first()
    if not t: return {'error': 'No active issue found'}, 404
    return execute_return(t, req_id)

@transactions_bp.route('/issue', methods=['POST'])
@jwt_required()
def issue_book():
    req_id = int(get_jwt_identity()); requester = User.query.get(req_id)
    data = request.get_json()
    uid = data.get('user_id', req_id)
    if requester.role not in ['admin','librarian'] and uid != req_id:
        return jsonify({'error':'Unauthorized'}),403
    res, status = issue_book_helper(uid, data['book_id'], req_id, data.get('loan_days',14))
    return jsonify(res), status

@transactions_bp.route('/return/<int:tid>', methods=['POST'])
@jwt_required()
def return_book(tid):
    t = Transaction.query.get_or_404(tid)
    req_id = int(get_jwt_identity())
    if t.status=='returned': return jsonify({'error':'Already returned'}),400
    res, status = execute_return(t, req_id)
    return jsonify(res), status

@transactions_bp.route('/reserve', methods=['POST'])
@jwt_required()
def reserve_book():
    uid = int(get_jwt_identity()); data = request.get_json()
    book = Book.query.get_or_404(data['book_id'])
    if Reservation.query.filter_by(user_id=uid,book_id=book.id,status='pending').first():
        return jsonify({'error':'Already reserved'}),400
    r = Reservation(user_id=uid,book_id=book.id,
                    expiry_date=datetime.utcnow()+timedelta(days=7))
    db.session.add(r); db.session.commit()
    return jsonify(r.to_dict()),201

@transactions_bp.route('/my-history', methods=['GET'])
@jwt_required()
def my_history():
    uid = int(get_jwt_identity())
    return jsonify([t.to_dict() for t in Transaction.query.filter_by(user_id=uid).order_by(Transaction.issue_date.desc()).all()])

@transactions_bp.route('/active', methods=['GET'])
@jwt_required()
def active_transactions():
    uid = int(get_jwt_identity()); user = User.query.get(uid)
    if user.role in ['admin','librarian']:
        txs = Transaction.query.filter_by(status='issued').all()
    else:
        txs = Transaction.query.filter_by(user_id=uid,status='issued').all()
    return jsonify([t.to_dict() for t in txs])

@transactions_bp.route('/overdue', methods=['GET'])
@jwt_required()
def overdue_transactions():
    uid = int(get_jwt_identity()); user = User.query.get(uid)
    if user.role not in ['admin','librarian']: return jsonify({'error':'Unauthorized'}),403
    now = datetime.utcnow()
    overdues = Transaction.query.filter(Transaction.status=='issued',Transaction.due_date<now).all()
    for t in overdues: t.status='overdue'
    db.session.commit()
    return jsonify([t.to_dict() for t in overdues])

@transactions_bp.route('/all', methods=['GET'])
@jwt_required()
def all_transactions():
    uid = int(get_jwt_identity()); user = User.query.get(uid)
    if user.role not in ['admin','librarian']: return jsonify({'error':'Unauthorized'}),403
    page = request.args.get('page',1,type=int)
    status = request.args.get('status','')
    q = Transaction.query
    if status: q = q.filter_by(status=status)
    p = q.order_by(Transaction.issue_date.desc()).paginate(page=page,per_page=25,error_out=False)
    return jsonify({'transactions':[t.to_dict() for t in p.items],'total':p.total,'pages':p.pages})

@transactions_bp.route('/pay-fine/<int:tid>', methods=['POST'])
@jwt_required()
def pay_fine(tid):
    t = Transaction.query.get_or_404(tid); t.fine_paid=True; db.session.commit()
    return jsonify(t.to_dict())

@transactions_bp.route('/my-reservations', methods=['GET'])
@jwt_required()
def my_reservations():
    uid = int(get_jwt_identity())
    return jsonify([r.to_dict() for r in Reservation.query.filter_by(user_id=uid).order_by(Reservation.reservation_date.desc()).all()])

@transactions_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    uid = int(get_jwt_identity())
    from models import Notification
    return jsonify([n.to_dict() for n in Notification.query.filter_by(user_id=uid).order_by(Notification.created_at.desc()).limit(20).all()])

@transactions_bp.route('/notifications/read', methods=['POST'])
@jwt_required()
def mark_read():
    uid = int(get_jwt_identity())
    from models import Notification
    Notification.query.filter_by(user_id=uid,is_read=False).update({'is_read':True})
    db.session.commit()
    return jsonify({'message':'done'})
