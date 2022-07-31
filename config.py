import os
from dotenv import load_dotenv
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'T_Park.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USE_SSL = 0
    MAIL_USERNAME = 'rating.nspt@gmail.com'
    MAIL_PASSWORD = '9610050908Dima'
    MAIL_DEFAULT_SENDER = 'flask@example.com'
    ADMINS = ['eternal-programmers@yandex.ru']
    USER_PER_PAGE = 15
    UPLOAD_FOLDER = '/app/static/images'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    CELERY_BROKER_URL = 'http://127.0.0.1:5000'
    CELERY_RESULT_BACKEND = 'http://127.0.0.1:5000'
    # BROKER_URL = 'redis://localhost:6379/0'
    # CELERY_RESULT_BACKEND = 'redis'

'''1m|MWoY?@S$kiEfO'''
