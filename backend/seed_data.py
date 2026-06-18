from datetime import datetime, timedelta
import random

def seed_database(app, db):
    from models import User, Book, Category, Author, Publisher, Transaction, Review
    with app.app_context():
        if db.session.query(User).count() > 0:
            return
        cats = {}
        for name, desc, icon in [
            ('Fiction','Novels','📚'),('Science','Scientific','🔬'),('Technology','Tech','💻'),
            ('History','Historical','🏛️'),('Philosophy','Philosophy','🤔'),('Mystery','Mystery','🔍'),
            ('Fantasy','Fantasy','🧙'),('Self-Help','Self-Help','🌱'),('Science Fiction','Sci-Fi','🚀'),
            ('Biography','Biographies','👤')]:
            c = Category(name=name,description=desc,icon=icon)
            db.session.add(c); db.session.flush(); cats[name]=c

        authors = []
        for name,bio,nat,yr in [
            ('George Orwell','Dystopian author','British',1903),
            ('J.K. Rowling','Harry Potter creator','British',1965),
            ('Stephen Hawking','Physicist','British',1942),
            ('Yuval Noah Harari','Historian','Israeli',1976),
            ('Agatha Christie','Mystery queen','British',1890),
            ('Frank Herbert','Sci-fi visionary','American',1920),
            ('J.R.R. Tolkien','Fantasy legend','British',1892),
            ('Dale Carnegie','Self-help','American',1888),
            ('Isaac Asimov','Sci-fi giant','American',1920),
            ('Fyodor Dostoevsky','Russian novelist','Russian',1821)]:
            a = Author(name=name,bio=bio,nationality=nat,birth_year=yr)
            db.session.add(a); db.session.flush(); authors.append(a)

        publishers = []
        for pname in ['Penguin Books','HarperCollins','Oxford Press','Random House','Simon & Schuster']:
            p = Publisher(name=pname)
            db.session.add(p); db.session.flush(); publishers.append(p)

        books_data = [
            ('1984',0,'Fiction','978-0451524935',1949,'A dystopian social science fiction novel.',328,'https://covers.openlibrary.org/b/id/8575171-L.jpg'),
            ('Animal Farm',0,'Fiction','978-0451526342',1945,'A political allegory about a farm revolt.',112,'https://covers.openlibrary.org/b/id/8739161-L.jpg'),
            ("Harry Potter and the Sorcerer's Stone",1,'Fantasy','978-0439708180',1997,'A young boy discovers he is a wizard.',309,'https://covers.openlibrary.org/b/id/10110415-L.jpg'),
            ('A Brief History of Time',2,'Science','978-0553380163',1988,'Cosmology explained for everyone.',212,'https://covers.openlibrary.org/b/id/8108538-L.jpg'),
            ('Sapiens',3,'History','978-0062316097',2011,'A bold history of humankind.',443,'https://covers.openlibrary.org/b/id/9255566-L.jpg'),
            ('Murder on the Orient Express',4,'Mystery','978-0062693662',1934,'Poirot investigates a luxury train murder.',256,'https://covers.openlibrary.org/b/id/8232502-L.jpg'),
            ('Dune',5,'Science Fiction','978-0441013593',1965,'Epic interstellar saga on a desert planet.',688,'https://covers.openlibrary.org/b/id/7772709-L.jpg'),
            ('The Lord of the Rings',6,'Fantasy','978-0618640157',1954,'The epic quest to destroy the One Ring.',1178,'https://covers.openlibrary.org/b/id/9255566-L.jpg'),
            ('How to Win Friends and Influence People',7,'Self-Help','978-0671027032',1936,'Timeless advice on building relationships.',288,'https://covers.openlibrary.org/b/id/8091016-L.jpg'),
            ('Foundation',8,'Science Fiction','978-0553293357',1951,'The decline and rebirth of a galactic empire.',244,'https://covers.openlibrary.org/b/id/7942660-L.jpg'),
            ('Crime and Punishment',9,'Fiction','978-0486415871',1866,'Psychological journey through guilt and redemption.',551,'https://covers.openlibrary.org/b/id/8235167-L.jpg'),
            ('Homo Deus',3,'Philosophy','978-0062464316',2015,"A vision of humanity's future.",450,'https://covers.openlibrary.org/b/id/8739161-L.jpg'),
            ('The Hobbit',6,'Fantasy','978-0547928227',1937,'Bilbo Baggins on an unexpected adventure.',310,'https://covers.openlibrary.org/b/id/7772709-L.jpg'),
            ('I Robot',8,'Science Fiction','978-0553294385',1950,'Classic robot ethics short stories.',256,'https://covers.openlibrary.org/b/id/8232502-L.jpg'),
            ('The ABC Murders',4,'Mystery','978-0062073600',1936,'An alphabetical series of murders.',256,'https://covers.openlibrary.org/b/id/8575171-L.jpg'),
            ('21 Lessons for the 21st Century',3,'Philosophy','978-0525512172',2018,'Key challenges facing humanity today.',352,'https://covers.openlibrary.org/b/id/9255566-L.jpg'),
            ('The Brothers Karamazov',9,'Fiction','978-0374528379',1880,'A philosophical novel of faith and doubt.',824,'https://covers.openlibrary.org/b/id/8739161-L.jpg'),
            ('Children of Dune',5,'Science Fiction','978-0441104024',1976,'The continuation of the Dune saga.',444,'https://covers.openlibrary.org/b/id/7772709-L.jpg'),
            ('The Silmarillion',6,'Fantasy','978-0618391110',1977,'The mythology of Middle-earth.',365,'https://covers.openlibrary.org/b/id/9255566-L.jpg'),
            ('And Then There Were None',4,'Mystery','978-0312330873',1939,'Ten strangers on an island are killed one by one.',264,'https://covers.openlibrary.org/b/id/8232502-L.jpg'),
        ]
        books = []
        for title,aidx,cat,isbn,year,desc,pages,cover in books_data:
            b = Book(title=title,author_id=authors[aidx].id,category_id=cats[cat].id,
                    publisher_id=random.choice(publishers).id,isbn=isbn,published_year=year,
                    description=desc,pages=pages,cover_image=cover,
                    total_copies=random.randint(3,8),available_copies=random.randint(1,5),
                    language='English',tags=cat)
            db.session.add(b); db.session.flush(); books.append(b)

        admin = User(username='admin',email='admin@library.com',full_name='Admin User',role='admin',is_active=True)
        admin.set_password('admin123'); db.session.add(admin); db.session.flush()

        librarian = User(username='librarian',email='librarian@library.com',full_name='Jane Smith',role='librarian',is_active=True)
        librarian.set_password('lib123'); db.session.add(librarian); db.session.flush()

        members = []
        for uname,email,fname in [('alice','alice@email.com','Alice Johnson'),
                                   ('bob','bob@email.com','Bob Williams'),
                                   ('charlie','charlie@email.com','Charlie Brown'),
                                   ('diana','diana@email.com','Diana Prince'),
                                   ('evan','evan@email.com','Evan Davis')]:
            m = User(username=uname,email=email,full_name=fname,role='member',is_active=True)
            m.set_password('pass123'); db.session.add(m); db.session.flush(); members.append(m)

        statuses = ['returned','returned','returned','issued','overdue']
        for _ in range(80):
            days_ago = random.randint(1,365)
            issue_date = datetime.utcnow()-timedelta(days=days_ago)
            due_date = issue_date+timedelta(days=14)
            status = random.choice(statuses)
            return_date = due_date+timedelta(days=random.randint(-5,10)) if status=='returned' else None
            fine = max(0,(return_date-due_date).days*2.0) if return_date and return_date>due_date else 0.0
            t = Transaction(user_id=random.choice(members).id,book_id=random.choice(books).id,
                           issue_date=issue_date,due_date=due_date,return_date=return_date,
                           status=status,fine_amount=fine,fine_paid=random.choice([True,False]))
            db.session.add(t)

        for book in random.sample(books,10):
            for member in random.sample(members,random.randint(1,3)):
                r = Review(user_id=member.id,book_id=book.id,rating=random.randint(3,5),comment='Great book!')
                db.session.add(r)

        db.session.commit()
        print("Database seeded!")
