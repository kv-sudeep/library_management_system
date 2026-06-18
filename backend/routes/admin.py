from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Book, Transaction, Category, Author, Publisher
from extensions import db
import io

admin_bp = Blueprint('admin', __name__)

def req_admin():
    u = User.query.get(int(get_jwt_identity()))
    return u if u and u.role=='admin' else None

@admin_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    if not req_admin(): return jsonify({'error':'Unauthorized'}),403
    d = request.get_json()
    c = Category(name=d['name'],description=d.get('description'),icon=d.get('icon'))
    db.session.add(c); db.session.commit(); return jsonify(c.to_dict()),201

@admin_bp.route('/categories/<int:cid>', methods=['PUT'])
@jwt_required()
def update_category(cid):
    if not req_admin(): return jsonify({'error':'Unauthorized'}),403
    c = Category.query.get_or_404(cid); d = request.get_json()
    for f in ['name','description','icon']:
        if f in d: setattr(c,f,d[f])
    db.session.commit(); return jsonify(c.to_dict())

@admin_bp.route('/authors', methods=['POST'])
@jwt_required()
def create_author():
    if not req_admin(): return jsonify({'error':'Unauthorized'}),403
    d = request.get_json()
    a = Author(name=d['name'],bio=d.get('bio'),nationality=d.get('nationality'),birth_year=d.get('birth_year'))
    db.session.add(a); db.session.commit(); return jsonify(a.to_dict()),201

@admin_bp.route('/publishers', methods=['POST'])
@jwt_required()
def create_publisher():
    if not req_admin(): return jsonify({'error':'Unauthorized'}),403
    d = request.get_json()
    p = Publisher(name=d['name'],address=d.get('address'),website=d.get('website'))
    db.session.add(p); db.session.commit(); return jsonify(p.to_dict()),201

@admin_bp.route('/system-stats', methods=['GET'])
@jwt_required()
def system_stats():
    if not req_admin(): return jsonify({'error':'Unauthorized'}),403
    return jsonify({
        'total_books':Book.query.count(),'total_users':User.query.count(),
        'total_transactions':Transaction.query.count(),'total_categories':Category.query.count(),
        'total_authors':Author.query.count(),'total_publishers':Publisher.query.count(),
    })

@admin_bp.route('/export/transactions', methods=['GET'])
@jwt_required()
def export_transactions():
    if not req_admin(): return jsonify({'error':'Unauthorized'}),403
    try:
        import openpyxl
        txs = Transaction.query.order_by(Transaction.issue_date.desc()).all()
        wb = openpyxl.Workbook(); ws = wb.active; ws.title='Transactions'
        ws.append(['ID','User','Book','Issue Date','Due Date','Return Date','Status','Fine','Fine Paid'])
        for t in txs:
            ws.append([t.id,t.user.username if t.user else '',t.book.title if t.book else '',
                      str(t.issue_date)[:10] if t.issue_date else '',
                      str(t.due_date)[:10] if t.due_date else '',
                      str(t.return_date)[:10] if t.return_date else '',
                      t.status,t.fine_amount,t.fine_paid])
        buf = io.BytesIO(); wb.save(buf); buf.seek(0)
        return send_file(buf,mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True,download_name='transactions.xlsx')
    except Exception as e:
        return jsonify({'error':str(e)}),500
