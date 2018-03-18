from . import bp
from .forms import CommentForm
from application.models import Book, Comment
from flask import request, render_template
from application import r


@bp.route('/<int:book_id>')
def index(book_id):
    form = CommentForm()
    book = Book.query.get_or_404(book_id)
    same_author_books = Book.query.filter_by(author=book.author).filter(Book.id != book.id)
    return render_template('book/index.html', book=book, form=form, same_author_books=same_author_books)


@bp.route('/<int:book_id>/comments')
def comments(book_id):
    form = CommentForm()
    book = Book.query.get_or_404(book_id)
    page = request.args.get('page', 1, type=int)
    pagination = book.comments.order_by(Comment.timestamp.desc()).paginate(page, 10, False)
    same_author_books = Book.query.filter_by(author=book.author).filter(Book.id != book.id)
    return render_template('book/comments.html', book=book, form=form, pagination=pagination, comments=pagination.items, same_author_books=same_author_books)


@bp.route('/<int:book_id>/same_author')
def same_author(book_id):
    form = CommentForm()
    book = Book.query.get_or_404(book_id)
    same_author_books = Book.query.filter_by(author=book.author).filter(Book.id != book.id)
    return render_template('book/same_author.html', book=book, form=form, same_author_books=same_author_books)


@bp.route('/<int:book_id>/similar_books')
def similar_books(book_id):
    form = CommentForm()
    book = Book.query.get_or_404(book_id)
    res = r.hgetall(book_id)
    same_author_books = Book.query.filter_by(author=book.author).filter(Book.id != book.id)
    si_books = []
    if res:
        for key, value in res.items():
            si_books.append((Book.query.get(key), float(value)*100))

    return render_template('book/similar_books.html', book=book, si_books=si_books, same_author_books=same_author_books, form=form)