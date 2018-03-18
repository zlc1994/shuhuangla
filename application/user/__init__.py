from flask import Blueprint


bp = Blueprint('user', __name__)


from application.user import routes
