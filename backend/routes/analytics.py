from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Transaction, Book, User, Category, Review, Reservation
from extensions import db
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import numpy as np
from sklearn.linear_model import LinearRegression

analytics_bp = Blueprint('analytics', __name__)

def staff_only():
    uid = int(get_jwt_identity())
    u = User.query.get(uid)
    return u if u and u.role in ['admin','librarian'] else None

@analytics_bp.route('/kpis', methods=['GET'])
@jwt_required()
def get_kpis():
    if not staff_only(): return jsonify({'error':'Unauthorized'}),403
    now = datetime.utcnow(); last30 = now - timedelta(days=30)
    return jsonify({
        'total_books': Book.query.count(),
        'total_users': User.query.filter_by(role='member').count(),
        'issued_books': Transaction.query.filter_by(status='issued').count(),
        'returned_books': Transaction.query.filter_by(status='returned').count(),
        'overdue_books': Transaction.query.filter(Transaction.status=='issued',Transaction.due_date<now).count(),
        'pending_reservations': Reservation.query.filter_by(status='pending').count(),
        'total_fines': round(db.session.query(db.func.sum(Transaction.fine_amount)).scalar() or 0,2),
        'unpaid_fines': round(db.session.query(db.func.sum(Transaction.fine_amount)).filter_by(fine_paid=False).scalar() or 0,2),
        'available_books': db.session.query(db.func.sum(Book.available_copies)).scalar() or 0,
        'new_users_month': User.query.filter(User.membership_date>=last30).count(),
        'new_transactions_month': Transaction.query.filter(Transaction.issue_date>=last30).count(),
    })

@analytics_bp.route('/most-borrowed', methods=['GET'])
@jwt_required()
def most_borrowed():
    if not staff_only(): return jsonify({'error':'Unauthorized'}),403
    limit = request.args.get('limit',10,type=int)
    rows = db.session.query(Book.id,Book.title,db.func.count(Transaction.id).label('cnt'))\
        .join(Transaction).group_by(Book.id).order_by(db.func.count(Transaction.id).desc()).limit(limit).all()
    return jsonify([{'book_id':r.id,'title':r.title,'borrow_count':r.cnt} for r in rows])

@analytics_bp.route('/least-borrowed', methods=['GET'])
@jwt_required()
def least_borrowed():
    if not staff_only(): return jsonify({'error':'Unauthorized'}),403
    books = Book.query.all()
    data = sorted([{'book_id':b.id,'title':b.title,'borrow_count':len(b.transactions)} for b in books],key=lambda x:x['borrow_count'])
    return jsonify(data[:10])

@analytics_bp.route('/monthly-trends', methods=['GET'])
@jwt_required()
def monthly_trends():
    if not staff_only(): return jsonify({'error':'Unauthorized'}),403
    txs = Transaction.query.filter(Transaction.issue_date>=datetime.utcnow()-timedelta(days=365)).all()
    monthly = defaultdict(int)
    for t in txs: monthly[t.issue_date.strftime('%Y-%m')] += 1
    s = sorted(monthly.items())
    return jsonify({'labels':[x[0] for x in s],'data':[x[1] for x in s]})

@analytics_bp.route('/category-analysis', methods=['GET'])
@jwt_required()
def category_analysis():
    if not staff_only(): return jsonify({'error':'Unauthorized'}),403
    rows = db.session.query(Category.name,db.func.count(Transaction.id).label('cnt'))\
        .join(Book,Book.category_id==Category.id).join(Transaction).group_by(Category.id).all()
    return jsonify({'labels':[r.name for r in rows],'data':[r.cnt for r in rows]})

@analytics_bp.route('/demand-forecast', methods=['GET'])
@jwt_required()
def demand_forecast():
    if not staff_only(): return jsonify({'error':'Unauthorized'}),403
    txs = Transaction.query.filter(Transaction.issue_date>=datetime.utcnow()-timedelta(days=365)).all()
    monthly = defaultdict(int)
    for t in txs: monthly[t.issue_date.strftime('%Y-%m')] += 1
    s = sorted(monthly.items())
    if len(s) < 3: return jsonify({'forecast':[],'historical':[],'trend':'unknown'})
    X = np.array(range(len(s))).reshape(-1,1)
    y = np.array([v for _,v in s])
    m = LinearRegression().fit(X,y)
    future_X = np.array(range(len(s),len(s)+6)).reshape(-1,1)
    preds = m.predict(future_X).tolist()
    last = datetime.strptime(s[-1][0],'%Y-%m')
    future_labels = [(last+timedelta(days=30*i)).strftime('%Y-%m') for i in range(1,7)]
    return jsonify({
        'historical':{'labels':[x[0] for x in s],'data':[x[1] for x in s]},
        'forecast':{'labels':future_labels,'data':[max(0,round(p)) for p in preds]},
        'trend':'increasing' if m.coef_[0]>0 else 'decreasing'
    })

@analytics_bp.route('/fine-report', methods=['GET'])
@jwt_required()
def fine_report():
    if not staff_only(): return jsonify({'error':'Unauthorized'}),403
    total = db.session.query(db.func.sum(Transaction.fine_amount)).scalar() or 0
    paid = db.session.query(db.func.sum(Transaction.fine_amount)).filter_by(fine_paid=True).scalar() or 0
    overdue_cnt = Transaction.query.filter(Transaction.status.in_(['issued','overdue']),Transaction.due_date<datetime.utcnow()).count()
    return jsonify({'total_fines':round(total,2),'paid_fines':round(paid,2),'unpaid_fines':round(total-paid,2),'overdue_count':overdue_cnt})

@analytics_bp.route('/trending', methods=['GET'])
def trending():
    since = datetime.utcnow()-timedelta(days=7)
    rows = db.session.query(Book.id,Book.title,Book.cover_image,db.func.count(Transaction.id).label('cnt'))\
        .join(Transaction).filter(Transaction.issue_date>=since).group_by(Book.id)\
        .order_by(db.func.count(Transaction.id).desc()).limit(8).all()
    return jsonify([{'id':r.id,'title':r.title,'cover_image':r.cover_image,'borrow_count':r.cnt} for r in rows])

@analytics_bp.route('/user-reading-habits', methods=['GET'])
@jwt_required()
def user_reading_habits():
    if not staff_only(): return jsonify({'error':'Unauthorized'}),403
    total_t = Transaction.query.count()
    total_u = max(User.query.filter_by(role='member').count(),1)
    top = db.session.query(User.username,User.full_name,db.func.count(Transaction.id).label('cnt'))\
        .join(Transaction,Transaction.user_id==User.id).group_by(User.id)\
        .order_by(db.func.count(Transaction.id).desc()).limit(10).all()
    txs = Transaction.query.filter(Transaction.issue_date!=None).all()
    dow = Counter([t.issue_date.strftime('%A') for t in txs])
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    return jsonify({
        'avg_books_per_user': round(total_t/total_u,2),
        'top_readers': [{'username':r.username,'full_name':r.full_name,'count':r.cnt} for r in top],
        'day_of_week': {'labels':days,'data':[dow.get(d,0) for d in days]}
    })

@analytics_bp.route('/inventory-forecast', methods=['GET'])
@jwt_required()
def inventory_forecast():
    if not staff_only(): return jsonify({'error':'Unauthorized'}),403
    books = Book.query.all()
    recs = []
    for b in books:
        rate = len(b.transactions)/max(b.total_copies,1)
        if rate>1.5 and b.available_copies==0:
            recs.append({'book_id':b.id,'title':b.title,'borrow_rate':round(rate,2),
                         'current_copies':b.total_copies,'suggested_purchase':min(int(rate),5)})
    return jsonify(sorted(recs,key=lambda x:x['borrow_rate'],reverse=True)[:10])
