import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or '2222'
    CSV = os.path.join(basedir, 'comments.csv')

    # for database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BOOK_INFO = os.path.join(basedir, 'items.json')
    REDIS_URL = "redis://localhost:6379/0"
    RQ_REDIS_URL = "redis://localhost:6379/1"

    # for email
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['2499518552@qq.com', '657386160@qq.com']
    

class DevelopConfig(Config):
    DEBUG = True
    # for database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://zlc:foo@sg2/shuhuang'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = "redis://localhost:6379/0"
    RQ_REDIS_URL = "redis://localhost:6379/1"


class EmailJobConfig(Config):
    SERVER_NAME = '192.168.2.22:5000'

