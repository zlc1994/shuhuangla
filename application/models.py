from application import db, login
from config import Config
import arrow
from sqlalchemy_utils import ArrowType
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import re
import time
import jwt


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(ArrowType, default=arrow.utcnow)
    join_time = db.Column(ArrowType, default=arrow.utcnow)
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=3600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time.time() + expires_in},
            Config.SECRET_KEY, algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, Config.SECRET_KEY, algorithm='HS256')['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_comments(self):
        return Comment.query.join(
            followers, (followers.c.followed_id == Comment.user_id)).filter(
                followers.c.follower_id == self.id).order_by(
                    Comment.timestamp.desc())


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bookname = db.Column(db.String(64), index=True)
    author = db.Column(db.String(64), index=True)
    tag = db.Column(db.String(64), index=True)
    book_id = db.Column(db.String(64), index=True)
    words = db.Column(db.Integer)
    chapters = db.Column(db.Integer)
    cover = db.Column(db.Text())
    pc_url = db.Column(db.Text())
    m_url = db.Column(db.Text())
    source = db.Column(db.String(64))
    intro = db.Column(db.Text())
    last_update = db.Column(ArrowType, index=True)
    last_chapter = db.Column(db.String(256))
    avg = db.Column(db.Float, default=0.0)
    comments = db.relationship('Comment', backref='book', lazy='dynamic')

    def __repr__(self):
        return '<Book {}>'.format(self.bookname)

    @staticmethod
    def insert_book():
        import pymongo
        client = pymongo.MongoClient(host='sg2')
        m_db = client['items']
        for item in m_db['books'].find():
            if len(item) == 14:
                try:
                    b = Book(
                        bookname=item['name'],
                        book_id=item['book_id'],
                        chapters=int(re.search('\d+', item['chapters']).group(0)),
                        words=int(re.search('\d+', item['words']).group(0)),
                        author=item['author'],
                        tag=item['tag'],
                        cover=item['cover'],
                        pc_url=item['pc_url'],
                        m_url=item['m_url'],
                        source=item['source'],
                        intro=item['info'],
                        last_update=arrow.get(item['last_update'], 'YY/MM/DD HH:mm').replace(tzinfo='Asia/Shanghai'),
                        last_chapter=item['last_chapter']
                    )
                    db.session.add(b)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    db.session.rollback()

    def set_avg(self):
        total = 0
        count = 0
        for c in self.comments:
            total += c.score
            count += 1
        if count:
            self.avg = total/count


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
