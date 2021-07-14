from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # about_me = db.Column(db.String(256))
    birth_date = db.Column(db.DateTime)
    grades = db.relationship('Grade', backref='user', lazy='dynamic')
    # team = db.Column(db.String(32))
    #grade = db.relationship('Expert', secondary='grade', backref=db.backref('user', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<Пользователь {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Expert(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(64))
    grades = db.relationship('Grade', backref='expert', lazy='dynamic')
    weight = db.Column(db.Boolean, default=1.0)
    quantity = db.Column(db.Integer, default=0)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    def __repr__(self):
        return 'Эксперт {}'.format(self.username)


class Grade(db.Model):
    __tablename__ = 'grade'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    expert_id = db.Column(db.String(64), db.ForeignKey('expert.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    parameter_1 = db.Column(db.Integer)
    parameter_2 = db.Column(db.Integer)
    parameter_3 = db.Column(db.Integer)
    parameter_4 = db.Column(db.Integer)
    parameter_5 = db.Column(db.Integer)

    def __repr__(self):
        return 'Оценка для {}'.format(self.user_id)
