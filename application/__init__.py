from flask import Flask, flash
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_redis import FlaskRedis
from flask_mail import Mail
import logging
from logging.handlers import SMTPHandler


db = SQLAlchemy()
migrate = Migrate(db)
mail = Mail()
r = FlaskRedis(decode_responses=True)
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = '请先登入'
login.login_message_category = 'is-primary'


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'is-danger')


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # email error
    if not app.debug:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure=None
        if app.config['MAIL_USE_TLS']:
            secure=()
        mail_hanlder = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=app.config['ADMINS'][0],
            toaddrs=app.config['ADMINS'], subject='书荒啦出现错误啦',
            credentials=auth, secure=secure
        )
        mail_hanlder.setLevel(logging.ERROR)
        app.logger.addHandler(mail_hanlder)

    from application.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from application.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from application.user import bp as user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from application.book import bp as book_bp
    app.register_blueprint(book_bp, url_prefix='/book')

    from application.main import bp as main_bp
    app.register_blueprint(main_bp)

    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    r.init_app(app)
    return app
