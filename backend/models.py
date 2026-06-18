from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='member')
    full_name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    membership_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    avatar = db.Column(db.String(255))
    qr_code = db.Column(db.String(255))
    transactions = db.relationship('Transaction', foreign_keys='Transaction.user_id', backref='user', lazy=True)
    reservations = db.relationship('Reservation', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    wishlist = db.relationship('Wishlist', backref='user', lazy=True)
    def set_password(self, p): self.password_hash = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password_hash, p)
    def to_dict(self):
        return {'id':self.id,'username':self.username,'email':self.email,'role':self.role,
                'full_name':self.full_name,'phone':self.phone,
                'membership_date':self.membership_date.isoformat() if self.membership_date else None,
                'is_active':self.is_active,'avatar':self.avatar}

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    books = db.relationship('Book', backref='category', lazy=True)
    def to_dict(self):
        return {'id':self.id,'name':self.name,'description':self.description,'icon':self.icon,'book_count':len(self.books)}

class Author(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    bio = db.Column(db.Text)
    nationality = db.Column(db.String(100))
    birth_year = db.Column(db.Integer)
    books = db.relationship('Book', backref='author', lazy=True)
    def to_dict(self):
        return {'id':self.id,'name':self.name,'bio':self.bio,'nationality':self.nationality,'birth_year':self.birth_year}

class Publisher(db.Model):
    __tablename__ = 'publishers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.Text)
    website = db.Column(db.String(200))
    books = db.relationship('Book', backref='publisher', lazy=True)
    def to_dict(self):
        return {'id':self.id,'name':self.name,'address':self.address,'website':self.website}

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(300), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publishers.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    published_year = db.Column(db.Integer)
    description = db.Column(db.Text)
    cover_image = db.Column(db.String(500))
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)
    language = db.Column(db.String(50), default='English')
    pages = db.Column(db.Integer)
    tags = db.Column(db.String(500))
    location = db.Column(db.String(100))
    pdf_url = db.Column(db.String(500))
    is_digital = db.Column(db.Boolean, default=False)
    qr_code = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('Transaction', backref='book', lazy=True)
    reservations = db.relationship('Reservation', backref='book', lazy=True)
    reviews = db.relationship('Review', backref='book', lazy=True)
    wishlist_items = db.relationship('Wishlist', backref='book', lazy=True)
    def avg_rating(self):
        if not self.reviews: return 0
        return sum(r.rating for r in self.reviews)/len(self.reviews)
    def to_dict(self):
        return {'id':self.id,'isbn':self.isbn,'title':self.title,
                'author':self.author.to_dict() if self.author else None,
                'publisher':self.publisher.to_dict() if self.publisher else None,
                'category':self.category.to_dict() if self.category else None,
                'published_year':self.published_year,'description':self.description,
                'cover_image':self.cover_image,'total_copies':self.total_copies,
                'available_copies':self.available_copies,'language':self.language,
                'pages':self.pages,'tags':self.tags,'location':self.location,
                'is_digital':self.is_digital,'pdf_url':self.pdf_url,
                'avg_rating':round(self.avg_rating(),2),
                'review_count':len(self.reviews),'borrow_count':len(self.transactions)}

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='issued')
    fine_amount = db.Column(db.Float, default=0.0)
    fine_paid = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    issued_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    def to_dict(self):
        return {'id':self.id,'user_id':self.user_id,'book_id':self.book_id,
                'issue_date':self.issue_date.isoformat() if self.issue_date else None,
                'due_date':self.due_date.isoformat() if self.due_date else None,
                'return_date':self.return_date.isoformat() if self.return_date else None,
                'status':self.status,'fine_amount':self.fine_amount,'fine_paid':self.fine_paid,
                'book':self.book.to_dict() if self.book else None,
                'user':self.user.to_dict() if self.user else None}

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    reservation_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='pending')
    def to_dict(self):
        return {'id':self.id,'user_id':self.user_id,'book_id':self.book_id,
                'reservation_date':self.reservation_date.isoformat() if self.reservation_date else None,
                'expiry_date':self.expiry_date.isoformat() if self.expiry_date else None,
                'status':self.status,'book':self.book.to_dict() if self.book else None}

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'user_id':self.user_id,'book_id':self.book_id,
                'rating':self.rating,'comment':self.comment,'created_at':self.created_at.isoformat(),
                'user':{'username':self.user.username,'full_name':self.user.full_name} if self.user else None}

class Wishlist(db.Model):
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

class ReadingProgress(db.Model):
    __tablename__ = 'reading_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    current_page = db.Column(db.Integer, default=1)
    total_pages = db.Column(db.Integer)
    percent_complete = db.Column(db.Float, default=0.0)
    last_read_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'book_id'),)
    book = db.relationship('Book', backref='readers', lazy=True)
    def to_dict(self):
        return {'id':self.id,'user_id':self.user_id,'book_id':self.book_id,
                'current_page':self.current_page,'total_pages':self.total_pages,
                'percent_complete':self.percent_complete,
                'last_read_at':self.last_read_at.isoformat() if self.last_read_at else None,
                'completed':self.completed,
                'book':self.book.to_dict() if self.book else None}

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100))
    resource = db.Column(db.String(100))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'user_id':self.user_id,'action':self.action,
                'resource':self.resource,'details':self.details,
                'timestamp':self.timestamp.isoformat()}

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    type = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'title':self.title,'message':self.message,
                'type':self.type,'is_read':self.is_read,
                'created_at':self.created_at.isoformat()}
