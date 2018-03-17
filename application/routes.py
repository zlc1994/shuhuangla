from application import app, db, r
from flask import render_template, flash, redirect, url_for, request
from application.forms import LoginForm, RegistrationForm, SettingForm, CommentForm
from application.models import User, Comment, Book
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import arrow


@app.route('/')
@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page, 10, False)
    return render_template('index.html', title='首页', comments=pagination.items, pagination=pagination)


@app.route('/followed_posts')
@login_required
def followed_comments():
    page = request.args.get('page', 1, type=int)
    pagination = current_user.followed_comments().paginate(page, 10, False)
    return render_template('followed_comments.html', title='首页', comments=pagination.items, pagination=pagination)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码不正确')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
             next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='登入', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('登出成功！', 'is-success')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('恭喜，您已注册成功!')
        return redirect(url_for('login'))
    return render_template('register.html', title='注册', form=form)


@app.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.comments.order_by(Comment.timestamp.desc()).paginate(page, 10, False)
    return render_template('user.html', user=user, comments=pagination.items, pagination=pagination)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = arrow.utcnow()
        db.session.commit()


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
    elif request.method == 'GET':
        form.about_me.data = current_user.about_me
    return render_template('settings.html', form=form)


@app.route('/user/<username>/followed')
def followed(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, 10, False)
    return render_template('user_followed.html', user=user, people=pagination.items, pagination=pagination)


@app.route('/user/<username>/followers')
def followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, 10, False)
    return render_template('user_followers.html', user=user, people=pagination.items, pagination=pagination)


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('该用户不存在'.format(username), 'is-danger')
        return redirect(url_for('index'))
    if user == current_user:
        flash('你不能关注自己', 'is-danger')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('关注 {} 成功'.format(username), 'is-sucess')
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('用户 {} 不存在'.format(username), 'is-danger')
        return redirect(url_for('index'))
    if user == current_user:
        flash('你不能取消关注自己', 'is-danger')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('成功取消关注 {}'.format(username), 'is-success')
    return redirect(url_for('user', username=username))


@app.route('/book/<int:book_id>')
def book(book_id):
    form = CommentForm()
    book = Book.query.get_or_404(book_id)
    same_author_books = Book.query.filter_by(author=book.author).filter(Book.id != book.id)
    return render_template('book.html', book=book, form=form, same_author_books=same_author_books)


@app.route('/book/<int:book_id>/comments')
def book_comments(book_id):
    form = CommentForm()
    book = Book.query.get_or_404(book_id)
    page = request.args.get('page', 1, type=int)
    pagination = book.comments.order_by(Comment.timestamp.desc()).paginate(page, 10, False)
    same_author_books = Book.query.filter_by(author=book.author).filter(Book.id != book.id)
    return render_template('book_comments.html', book=book, form=form, pagination=pagination, comments=pagination.items, same_author_books=same_author_books)


@app.route('/book/<int:book_id>/sameauthor')
def same_author(book_id):
    form = CommentForm()
    book = Book.query.get_or_404(book_id)
    same_author_books = Book.query.filter_by(author=book.author).filter(Book.id != book.id)
    return render_template('same_author_books.html', book=book, form=form, same_author_books=same_author_books)


@app.route('/comment', methods=['POST'])
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
                flash('修改成功!')
            else:
                c = Comment(user=u, book=b, body=form.body.data, score=form.score.data)
                db.session.add(c)
                flash('评论成功')
            b.set_avg()
            db.session.commit()
        else:
            flash('该用户或书籍不存在')
            return redirect(url_for('index'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                ))
    return redirect(url_for('book', book_id=form.book_id.data))


@app.route('/allbooks')
def allbooks():
    page = request.args.get('page', 1, type=int)
    pagination = Book.query.order_by(Book.avg.desc()).paginate(page, 10, False)
    return render_template('allbooks.html', pagination=pagination, books=pagination.items)


@app.route('/book/<int:book_id>/similar_books')
def similar_books(book_id):
    form = CommentForm()
    book = Book.query.get_or_404(book_id)
    res = r.hgetall(book_id)
    same_author_books = Book.query.filter_by(author=book.author).filter(Book.id != book.id)
    si_books = []
    print(res)
    if res:
        for key, value in res.items():
            si_books.append((Book.query.get(key), float(value)*100))

    return render_template('similar_books.html', book=book, si_books=si_books, same_author_books=same_author_books, form=form)



