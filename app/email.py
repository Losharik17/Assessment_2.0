from threading import Thread
from flask import render_template, current_app
from flask_mail import Message
from sqlalchemy import create_engine
from app import mail
from app.main.functions import password_generator


def send_async_email(app, subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    from main import app
    Thread(target=send_async_email,
           args=(app, subject, sender, recipients, text_body, html_body)).start()


def send_mail_new(project_number, number, typ):
    from main import app
    Thread(target=async_mail_new,
           args=(app, project_number, number, typ)).start()


def async_mail_new(app, project_number, number, type):
    from app.models import Expert, User

    engine = create_engine("sqlite:////var/www/fastuser/data/www/rating.nspt.ru/T_Park.db")
    with app.app_context():
        if type == 'users':
            users = User.query.filter_by(project_number=project_number).all()
        elif type == 'experts':
            users = Expert.query.filter_by(project_number=project_number).all()
        else:
            return

        for i in range(number):
            users.pop(0)

        for user in users:
            passw = password_generator()
            engine.execute("UPDATE expert SET password_hash = ? WHERE email = ?",
                           passw, user.email)
            msg = Message('NSPT Ваш пароль', sender=current_app.config['MAIL_USERNAME'],
                          recipients=[user.email])
            msg.body = render_template('email/send_password.txt',
                                       user=user, password=passw)
            msg.html = render_template('email/send_password.html',
                                       user=user, password=passw)
            mail.send(msg)
