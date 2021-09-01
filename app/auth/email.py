from flask import render_template, current_app
from app.email import send_email


def send_password_reset_email(user):

    token = user.get_reset_password_token()
    send_email('NSPT Восстановление пароля',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def send_password_mail(user, password):
    send_email('NSPT Ваш пароль',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/send_password.txt',
                                         user=user, password=password),
               html_body=render_template('email/send_password.html',
                                         user=user, password=password))


def send_alert_mail(viewer, date, names):
    send_email('NSPT Статус проекта',
               sender=current_app.config['ADMINS'][0],
               recipients=[viewer.email],
               text_body=render_template('email/send_alert.txt',
                                         viewer=viewer, date=date, names= names),
               html_body=render_template('email/send_alert.html',
                                         viewer=viewer, date=date, names = names))


def send_role_update(user, role):
    send_email('[TPark] Изменение вашего статуса',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/send_role_update.txt',
                                         user=user, role=role),
               html_body=render_template('email/send_role_update.html',
                                         user=user, role=role))


def send_role_refuse(user):
    send_email('[TPark] Изменение вашего статуса',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/send_role_refuse.txt',
                                         user=user),
               html_body=render_template('email/send_role_refuse.html',
                                         user=user))