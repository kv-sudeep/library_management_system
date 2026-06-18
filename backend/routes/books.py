from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Book, Author, Publisher, Category, Review, Wishlist, User
from extensions import db

books_bp = Blueprint('books', __name__)

@books_bp.route('/', methods=['GET'])
def get_books():
    page = request.args.get('page',1,type=int)
    per_page = request.args.get('per_page',20,type=int)
    search = request.args.get('search','')
    category_id = request.args.get('category_id',type=int)
    sort_by = request.args.get('sort_by','title')
    available_only = request.args.get('available_only','false').lower()=='true'
    q = Book.query
    if search:
        q = q.filter(db.or_(Book.title.ilike(f'%{search}%'),Book.tags.ilike(f'%{search}%'),Book.description.ilike(f'%{search}%')))
    if category_id: q = q.filter_by(category_id=category_id)
    if available_only: q = q.filter(Book.available_copies>0)
    if sort_by=='newest': q = q.order_by(Book.created_at.desc())
    elif sort_by=='popular': q = q.order_by(Book.total_copies.desc())
    else: q = q.order_by(Book.title)
    p = q.paginate(page=page,per_page=per_page,error_out=False)
    return jsonify({'books':[b.to_dict() for b in p.items],'total':p.total,'pages':p.pages,'current_page':page})

@books_bp.route('/<int:bid>', methods=['GET'])
def get_book(bid):
    return jsonify(Book.query.get_or_404(bid).to_dict())

@books_bp.route('/', methods=['POST'])
@jwt_required()
def create_book():
    user = User.query.get(int(get_jwt_identity()))
    if user.role not in ['admin','librarian']: return jsonify({'error':'Unauthorized'}),403
    data = request.get_json()
    author_id = data.get('author_id')
    if not author_id and data.get('author_name'):
        a = Author(name=data['author_name'])
        db.session.add(a); db.session.flush(); author_id = a.id
    b = Book(title=data['title'],isbn=data.get('isbn'),author_id=author_id,
             publisher_id=data.get('publisher_id'),category_id=data.get('category_id'),
             published_year=data.get('published_year'),description=data.get('description'),
             cover_image=data.get('cover_image'),total_copies=data.get('total_copies',1),
             available_copies=data.get('available_copies',data.get('total_copies',1)),
             language=data.get('language','English'),pages=data.get('pages'),tags=data.get('tags'),
             location=data.get('location'),is_digital=data.get('is_digital',False),pdf_url=data.get('pdf_url'))
    db.session.add(b); db.session.commit()
    return jsonify(b.to_dict()),201

@books_bp.route('/<int:bid>', methods=['PUT'])
@jwt_required()
def update_book(bid):
    user = User.query.get(int(get_jwt_identity()))
    if user.role not in ['admin','librarian']: return jsonify({'error':'Unauthorized'}),403
    b = Book.query.get_or_404(bid); data = request.get_json()
    for f in ['title','isbn','description','cover_image','total_copies','available_copies',
              'language','pages','tags','location','published_year','category_id','author_id','publisher_id']:
        if f in data: setattr(b,f,data[f])
    db.session.commit(); return jsonify(b.to_dict())

@books_bp.route('/<int:bid>', methods=['DELETE'])
@jwt_required()
def delete_book(bid):
    user = User.query.get(int(get_jwt_identity()))
    if user.role!='admin': return jsonify({'error':'Unauthorized'}),403
    b = Book.query.get_or_404(bid); db.session.delete(b); db.session.commit()
    return jsonify({'message':'Deleted'})

@books_bp.route('/<int:bid>/reviews', methods=['GET'])
def get_reviews(bid):
    return jsonify([r.to_dict() for r in Review.query.filter_by(book_id=bid).all()])

@books_bp.route('/<int:bid>/reviews', methods=['POST'])
@jwt_required()
def add_review(bid):
    uid = int(get_jwt_identity()); data = request.get_json()
    ex = Review.query.filter_by(user_id=uid,book_id=bid).first()
    if ex:
        ex.rating=data.get('rating',ex.rating); ex.comment=data.get('comment',ex.comment)
        db.session.commit(); return jsonify(ex.to_dict())
    r = Review(user_id=uid,book_id=bid,rating=data['rating'],comment=data.get('comment',''))
    db.session.add(r); db.session.commit(); return jsonify(r.to_dict()),201

@books_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify([c.to_dict() for c in Category.query.all()])

@books_bp.route('/authors', methods=['GET'])
def get_authors():
    return jsonify([a.to_dict() for a in Author.query.all()])

@books_bp.route('/featured', methods=['GET'])
def get_featured():
    return jsonify([b.to_dict() for b in Book.query.order_by(Book.created_at.desc()).limit(12).all()])

@books_bp.route('/recommendations/<int:uid>', methods=['GET'])
@jwt_required()
def get_recommendations(uid):
    from models import Transaction
    from collections import Counter
    txs = Transaction.query.filter_by(user_id=uid).all()
    cats = [t.book.category_id for t in txs if t.book and t.book.category_id]
    borrowed = [t.book_id for t in txs]
    if cats:
        top = [c for c,_ in Counter(cats).most_common(3)]
        recs = Book.query.filter(Book.category_id.in_(top),~Book.id.in_(borrowed)).limit(10).all()
    else:
        recs = Book.query.order_by(Book.created_at.desc()).limit(10).all()
    return jsonify([b.to_dict() for b in recs])

@books_bp.route('/wishlist', methods=['GET'])
@jwt_required()
def get_wishlist():
    uid = int(get_jwt_identity())
    items = Wishlist.query.filter_by(user_id=uid).all()
    return jsonify([{'id':w.id,'book':w.book.to_dict()} for w in items])

@books_bp.route('/wishlist/<int:bid>', methods=['POST'])
@jwt_required()
def add_wishlist(bid):
    uid = int(get_jwt_identity())
    if Wishlist.query.filter_by(user_id=uid,book_id=bid).first():
        return jsonify({'message':'Already in wishlist'})
    db.session.add(Wishlist(user_id=uid,book_id=bid)); db.session.commit()
    return jsonify({'message':'Added'}),201

@books_bp.route('/wishlist/<int:bid>', methods=['DELETE'])
@jwt_required()
def remove_wishlist(bid):
    uid = int(get_jwt_identity())
    w = Wishlist.query.filter_by(user_id=uid,book_id=bid).first()
    if w: db.session.delete(w); db.session.commit()
    return jsonify({'message':'Removed'})

@books_bp.route('/lookup/<isbn>', methods=['GET'])
@jwt_required()
def lookup_isbn(isbn):
    user = User.query.get(int(get_jwt_identity()))
    if user.role not in ['admin', 'librarian']: return jsonify({'error': 'Unauthorized'}), 403
    import requests
    try:
        resp = requests.get(f'https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data', timeout=10)
        data = resp.json()
        key = f'ISBN:{isbn}'
        if key not in data:
            return jsonify({'error': 'No book found for this ISBN'}), 404
        b = data[key]
        authors = [a.get('name') for a in b.get('authors', [])]
        pub_year = b.get('publish_date', '')
        if pub_year:
            import re
            m = re.search(r'\d{4}', str(pub_year))
            pub_year = int(m.group(0)) if m else None
        cov = b.get('cover', {})
        return jsonify({
            'title': b.get('title', ''),
            'author_name': ', '.join(authors) if authors else '',
            'published_year': pub_year,
            'cover_image': cov.get('large') or cov.get('medium') or '',
            'pages': b.get('number_of_pages', None)
        })
    except Exception as e:
        return jsonify({'error': 'Failed to fetch data from Open Library'}), 500

