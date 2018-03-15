from application import app, db
from flask import render_template, flash, redirect, url_for, request
from application.forms import LoginForm, RegistrationForm, SettingForm
from application.models import User, Comment
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import arrow
from sqlalchemy import desc


@app.route('/')
@app.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(desc(Comment.timestamp)).paginate(page, 10, False)
    return render_template('index.html', title='首页', comments=pagination.items, pagination=pagination)

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
    pagination = user.comments.order_by(desc(Comment.timestamp)).paginate(page, 10, False)
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
        flash('该用户不存在'.format(username), 'is-danger')
        return redirect(url_for('index'))
    if user == current_user:
        flash('你不能取消关注自己', 'is-danger')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('成功取消关注'.format(username), 'is-success')
    return redirect(url_for('user', username=username))