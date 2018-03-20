from threading import Thread

from flask import render_template, current_app
from flask_mail import Message

from application import mail
from config import Config


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[书荒啦] 重置密码', sender=Config.ADMINS[0], recipients=[user.email],
               text_body=render_template('email/reset_password_request.txt', user=user, token=token),
               html_body=render_template('email/reset_password_request.html', user=user, token=token))
