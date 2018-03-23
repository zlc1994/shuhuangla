from flask import render_template
from application.email import send_email
from application import rq, create_app
from config import EmailJobConfig


@rq.job('email', timeout=60)
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    app = create_app(config_class=EmailJobConfig)
    with app.app_context():
        send_email('[书荒啦] 重置密码', sender=app.config['ADMINS'][0], recipients=[user.email],
                   text_body=render_template('email/reset_password_request.txt', user=user, token=token),
                   html_body=render_template('email/reset_password_request.html', user=user, token=token))