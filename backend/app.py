from flask import Flask
from flask_cors import CORS
from datetime import timedelta
from extensions import db, jwt

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'library-secret-key-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-library-2024'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, origins="*")
    from routes.auth import auth_bp
    from routes.books import books_bp
    from routes.users import users_bp
    from routes.transactions import transactions_bp
    from routes.analytics import analytics_bp
    from routes.admin import admin_bp
    from routes.qr import qr_bp
    from routes.digital import digital_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(books_bp, url_prefix='/api/books')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(transactions_bp, url_prefix='/api/transactions')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(qr_bp, url_prefix='/api/qr')
    app.register_blueprint(digital_bp, url_prefix='/api/digital')
    with app.app_context():
        db.create_all()
        from seed_data import seed_database
        seed_database(app, db)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, port=5000, host='0.0.0.0')
