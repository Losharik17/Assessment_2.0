"""
from threading import Thread
from flask_mail import Message
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    from main import app
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(app, msg)).start()
"""

import smtplib


def send_email(host, subject, to_addr, from_addr, body_text):

    BODY = "\r\n".join((
        "From: %s" % from_addr,
        "To: %s" % to_addr,
        "Subject: %s" % subject,
        "",
        body_text
    ))

    server = smtplib.SMTP(host)
    server.sendmail(from_addr, [to_addr], BODY)
    server.quit()


if __name__ == "__main__":
    host = "mySMTP.server.com"
    subject = "Test email from Python"
    to_addr = "mike@someAddress.org"
    from_addr = "python@mydomain.com"
    body_text = "Python rules them all!"
    send_email(host, subject, to_addr, from_addr, body_text)
