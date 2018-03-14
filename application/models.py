from application import db, login
import arrow
from sqlalchemy_utils import ArrowType
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    comments = db.relationship('Comment', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookname = db.Column(db.String(64), index=True)
    author = db.Column(db.String(64), index=True)
    comments = db.relationship('Comment', backref='book', lazy='dynamic')

    def __repr__(self):
        return '<Book {}>'.format(self.bookname)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text())
    score = db.Column(db.Integer)
    timestamp = db.Column(ArrowType, index=True, default=arrow.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))

    def __repr__(self):
        return '<Comment score: {0}, body: {1}>'.format(self.score, self.body)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))