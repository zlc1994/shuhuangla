from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_redis import FlaskRedis


db = SQLAlchemy()
migrate = Migrate(db)
r = FlaskRedis(decode_responses=True)
login = LoginManager()
login.login_view = 'login'
login.login_message = '请先登入'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

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
    migrate.init_app(app, db)
    login.init_app(app)
    r.init_app(app)
    return app
