from flask import current_app, render_template
from app.models import Expert, User
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from platform import python_version
from threading import Thread
from email.header import Header
from app import inbox


def mail_test():
    Thread(target=async_mail_proj, args=(current_app.config['MAIL_USERNAME'],)).start()
    return 'Mail test is started'


def send_mail_proj(project_id, role):
    if role == 'expert':
        recipients = Expert.query.filter_by(project_id=project_id).all()
    else:
        recipients = User.query.filter_by(project_id=project_id).all()

    sender = current_app.config['MAIL_USERNAME']
    Thread(target=async_mail_proj, args=(sender, recipients)).start()


@inbox.collate
def async_mail_proj(sender):
    mail = smtplib.SMTP_SSL('smtp.yandex.ru', 587)
    mail.login(sender, '9610050908Dima_')

    for recipient in range(1000):
        mail_subject = 'Ваш пароль'
        text_body = f'Здравствуйте, {recipient}, вам'
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        # msg.attach(MIMEText(html, 'html', 'utf-8'))
        msg['Subject'] = Header(mail_subject, 'utf-8')
        msg['From'] = f'NSPT <{sender}>'
        msg['Reply-To'] = sender
        msg['Return-Path'] = sender
        msg['X-Mailer'] = 'Python/' + (python_version())
        x = rand_email()
        msg['To'] = x
        mail.sendmail(sender, x, msg.as_string().encode("utf-8"))
        print('Отправлено сообщение',  recipient)

    # html_body = render_template('email/send_password.html',
    #                             user='dfsgd', password='dsgfgdseret')

    mail_subject = 'Тема сообщения'
    text_body = 'Текст сообщения'
    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    # msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    msg['Subject'] = Header(mail_subject, 'utf-8')
    msg['From'] = f'NSPT <{sender}>'
    msg['Reply-To'] = sender
    msg['Return-Path'] = sender
    msg['X-Mailer'] = 'Python/' + (python_version())
    mail.sendmail(sender, 'tankustvotnycke@yandex.ru', msg.as_string().encode("utf-8"))
    mail.quit()
    print('Отправлено последнее сообщение')


letters = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n",
           "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", ]


def rand_email():
    from random import randint, choice
    str = ''
    for _ in range(randint(8, 12)):
        str += choice(letters)
    return str + '@yandex.ru'



def send_email(subject, sender, recipients, text_body, html_body):
    Thread(target=async_email, args=(subject, sender, recipients, text_body, html_body)).start()


@inbox.collate
def async_email(subject, sender, recipients, text_body, html_body):
    mail = smtplib.SMTP_SSL('smtp.yandex.ru')
    mail.login(sender, '9610050908Dima_')

    for recipient in recipients:
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = f'NSPT <{sender}>'
        msg['Reply-To'] = sender
        msg['Return-Path'] = sender
        msg['X-Mailer'] = 'Python/' + (python_version())
        msg['To'] = recipient
        mail.sendmail(sender, recipient, msg.as_string().encode("utf-8"))
    mail.quit()
