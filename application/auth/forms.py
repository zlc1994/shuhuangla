from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from application.models import User


class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='用户名为空')])
    password = PasswordField('密码', validators=[DataRequired(message='密码为空')])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登入')


class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='用户名为空')])
    email = StringField('邮箱', validators=[DataRequired(message='邮箱为空'), Email(message='邮箱格式不正确')])
    password = PasswordField('密码', validators=[DataRequired(message="密码为空")])
    password2 = PasswordField(
        '确认密码', validators=[DataRequired(message="确认密码为空"), EqualTo('password', message='两次密码不一致')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('用户名已被注册')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('邮箱已被注册')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('注册邮箱', validators=[DataRequired("请输入注册邮箱"), Email("邮箱格式不正确")])
    submit = SubmitField('重置密码')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('新密码', validators=[DataRequired(message='密码为空')])
    password2 = PasswordField(
    '确认密码', validators=[DataRequired(message="确认密码为空"), EqualTo('password')])
    submit = SubmitField('重置密码')