from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user
from . import bp
from .forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from application.models import User
from application import db, flash_errors
from application.email import send_password_reset_email


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或密码不正确', 'is-danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
             next_page = url_for('main.index')
        return redirect(next_page)
    else:
        flash_errors((form))
    return render_template('auth/login.html', title='登入', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    flash('登出成功！', 'is-success')
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('恭喜，您已注册成功!', 'is-success')
        return redirect(url_for('auth.login'))
    else:
        flash_errors(form)
    return render_template('auth/register.html', title='注册', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('请点击邮箱中的链接完成密码重置，如果没有收到邮件，请检查垃圾箱', 'is-success')
        else:
            flash('邮箱不存在', 'is-danger')
        return redirect(url_for('auth.login'))
    else:
        flash_errors(form)
    return render_template('auth/reset_password_request.html', title='重置密码', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('密码重置成功', 'is-success')
        return redirect(url_for('auth.login'))
    else:
        flash_errors(form)
    return render_template('auth/reset_password.html', form=form)