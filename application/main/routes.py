import arrow
from flask import render_template, redirect, jsonify, request, g, flash, url_for
from flask_login import login_required, current_user

from application import db, flash_errors, r
from application.book.forms import CommentForm
from application.models import Comment, Book, User
from .tasks import start_spider
from . import bp
from .forms import SearchForm, SettingForm, SubmitNewBookForm


@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, 10, False)
    total_users = User.query.count()
    total_books = Book.query.count()
    total_comments = Comment.query.count()
    return render_template('index.html', title='首页', comments=pagination.items, pagination=pagination,
                           total_users=total_users, total_books=total_books, total_comments=total_comments)


@bp.route('/followed_posts')
@login_required
def followed_comments():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.followed_comments().paginate(page, 10, False)
    return render_template('followed_comments.html', title='首页', comments=pagination.items, pagination=pagination)


@bp.before_app_request
def before_request():
    g.search_form = SearchForm()
    if current_user.is_authenticated:
        current_user.last_seen = arrow.utcnow()
        db.session.commit()


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('资料修改成功', 'is-success')
    elif request.method == 'GET':
        form.about_me.data = current_user.about_me
    else:
        flash_errors(form)
    return render_template('settings.html', form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('该用户不存在'.format(username), 'is-danger')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('你不能关注自己', 'is-danger')
        return redirect(url_for('user.index', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('关注 {} 成功'.format(username), 'is-sucess')
    return redirect(url_for('user.index', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户 {} 不存在'.format(username), 'is-danger')
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('你不能取消关注自己', 'is-danger')
        return redirect(url_for('user.index', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('成功取消关注 {}'.format(username), 'is-success')
    return redirect(url_for('user.index', username=username))


@bp.route('/comment', methods=['GET', 'POST'])
@login_required
def comment():
    form = CommentForm()
    if form.validate_on_submit():
        u = User.query.get(form.user_id.data)
        b = Book.query.get(form.book_id.data)
        if u and b:
            c = Comment.query.filter_by(user=u, book=b).first()
            if c:
                c.body = form.body.data
                c.score = form.score.data
                c.timestamp = arrow.utcnow()
                flash('修改成功!', 'is-success')
            else:
                c = Comment(user=u, book=b, body=form.body.data, score=form.score.data)
                db.session.add(c)
                flash('评论成功', 'is-success')
            b.set_avg()
            db.session.commit()
        else:
            flash('该用户或书籍不存在', 'is-danger')
            return redirect(url_for('main.index'))
    else:
        flash_errors(form)
    return redirect(url_for('book.index', book_id=form.book_id.data))


@bp.route('/allbooks')
def allbooks():
    page = request.args.get('page', 1, type=int)
    pagination = Book.query.order_by(Book.avg.desc()).paginate(page, 10, False)
    return render_template('allbooks.html', pagination=pagination, books=pagination.items)


@bp.route('/search', methods=['POST'])
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('main.index'))
    return redirect(url_for('main.search_results', q=g.search_form.q.data))


@bp.route('/search_results/<q>')
def search_results(q):
    page = request.args.get('page', 1, type=int)
    pagination = Book.query.filter(Book.bookname.contains(q)).order_by(Book.avg.desc()).paginate(page, 10, False)
    total_users = User.query.count()
    total_books = Book.query.count()
    total_comments = Comment.query.count()
    return render_template('search_results.html', results=pagination.items, pagination=pagination, q=q,
                           total_comments=total_comments, total_books=total_books, total_users=total_users)


@bp.route('/autocomplete')
def autocomplete():
    res = [book.bookname for book in Book.query.filter(Book.bookname.contains(request.args.get('term')))]
    return jsonify(res)


@bp.route('/submit_new_book', methods=['GET', 'POST'])
def submit_new_book():
    form = SubmitNewBookForm()
    if form.validate_on_submit():
        start_spider.queue(form.url.data)
        flash('任务已经提交到队列，这本书或许需要一些时间才能被搜索到', 'is-success')
    else:
        flash_errors(form)
    return render_template('submit_new_book.html', form=form)


@bp.route('/guess_you_like')
@login_required
def guess_you_like():
    total_users = User.query.count()
    total_books = Book.query.count()
    total_comments = Comment.query.count()
    comments = current_user.comments.all()
    already_read = {i.book_id: 1 for i in comments}
    total_si = {}
    total_sum = {}
    rec = []
    if comments is None:
        flash('您还没有评价任何小说，暂时无法为您推荐')
    for comment in comments:
        if r.exists(comment.book_id):
            for similar_book, value in r.hgetall(comment.book_id).items():
                similar_book = int(similar_book)
                value = float(value)
                if similar_book not in already_read:
                    total_si.setdefault(similar_book, 0)
                    total_sum.setdefault(similar_book, 0)

                    total_sum[similar_book] += value * comment.score
                    total_si[similar_book] += value

    for item in total_si:
        if total_si[item] and total_sum[item] / total_si[item] >= 3:
            rec.append((total_sum[item] / total_si[item], Book.query.get(item)))

    rec = sorted(rec, key=lambda x: x[0])
    rec = rec[:20]

    return render_template('guess_you_like.html', rec=rec, total_books=total_books, total_users=total_users,
                           total_comments=total_comments)
