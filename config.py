import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://zlc:1@localhost/shuhuang?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOK_INFO = os.path.join(basedir, 'items.json')
    REDIS_URL = "redis://localhost:6379/0"