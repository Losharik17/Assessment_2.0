from inbox import Inbox
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


inbox = Inbox()


@inbox.collate
def handle(to, sender):
    mail = smtplib.SMTP_SSL('smtp.yandex.ru')
    mail.login(sender, '9610050908Dima_')

    for recipient in to:
        recipient = 'tankustvotnycke@yandex.ru'
        mail_subject = 'Тема сообщения'
        text_body = 'Текст сообщения'
        msg = MIMEMultipart("alternative")

        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
        # msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        msg['Subject'] = Header(mail_subject, 'utf-8')
        msg['From'] = f'NSPT <{sender}>'
        msg['Reply-To'] = sender
        msg['Return-Path'] = sender
        # msg['X-Mailer'] = 'Python/' + (python_version())
        msg['To'] = recipient
        mail.sendmail(sender, recipient, msg.as_string().encode("utf-8"))
    mail.quit()


handle(['123'], 'dimanormanev@yandex.ru')

# Bind directly.
inbox.serve(address='0.0.0.0', port=4467)

