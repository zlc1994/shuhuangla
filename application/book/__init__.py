from flask import Blueprint


bp = Blueprint('book', __name__)


from application.book import routes