from . import bp
from flask import request, render_template
from application.models import User, Comment


@bp.route('/<username>')
def index(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.comments.order_by(Comment.timestamp.desc()).paginate(page, 10, False)
    return render_template('user/index.html', user=user, comments=pagination.items, pagination=pagination)


@bp.route('/<username>/followed')
def followed(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, 10, False)
    return render_template('user/followed.html', user=user, people=pagination.items, pagination=pagination)


@bp.route('/<username>/followers')
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, 10, False)
    return render_template('user/followers.html', user=user, people=pagination.items, pagination=pagination)