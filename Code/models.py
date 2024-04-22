from datetime import datetime
from flask_login import UserMixin
from controllers import db, login_manager
from datetime import timedelta, datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    create_date = db.Column(
        db.DateTime, nullable=False, default=datetime.now)
    

    def get_id(self):
        return (self.user_id)
    

class Section(db.Model):
    __tablename__ = "section"
    section_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    description = db.Column(db.Text)

class Book(db.Model):
    __tablename__ = "book"
    book_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # publish_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    author = db.Column(db.String(100), nullable=False)
    file_name = db.Column(db.String(100), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.section_id'), nullable=False)
    section = db.relationship('Section', backref=db.backref('books', lazy=True))

class IssuedBook(db.Model):
    __tablename__ = "issued_book"
    issued_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    return_date = db.Column(db.DateTime)


class BookRequest(db.Model):
    request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    request_date = db.Column(db.DateTime, nullable=False, default=datetime.now())
    return_date = db.Column(db.DateTime, nullable=False,default=(datetime.now() + timedelta(days=7)))
    status = db.Column(db.Boolean, nullable=False, default=True)


class Rating(db.Model):
    rating_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text)
    date_rated = db.Column(db.DateTime, nullable=False,default=datetime.now())
