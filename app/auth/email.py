from flask import render_template, current_app
from app.email import send_email


def send_password_reset_email(user):

    token = user.get_reset_password_token()
    send_email('[TPark] Восстановление пароля',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def send_password_mail(user, password):
    send_email('[TPark] Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/send_password.txt',
                                         user=user, password=password),
               html_body=render_template('email/send_password.html',
                                         user=user, password=password))