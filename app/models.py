from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import Integer
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    avatar = db.Column(db.String)
    password_hash = db.Column(db.String(128))
    # about_me = db.Column(db.String(256))
    birth_date = db.Column(db.Date)
    team = db.Column(db.String(32))
    grades = db.relationship('Grade', backref='user', lazy='dynamic')
    sum_grade_0 = db.Column(db.Float, default=0)
    sum_grade_1 = db.Column(db.Float, default=0)
    sum_grade_2 = db.Column(db.Float, default=0)
    sum_grade_3 = db.Column(db.Float, default=0)
    sum_grade_4 = db.Column(db.Float, default=0)
    sum_grade_all = db.Column(db.Float, default=0)

    # grade = db.relationship('Expert', secondary='grade', backref=db.backref('user', lazy='dynamic'), lazy='dynamic')

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

    def sum_grades(self):  # в принципе это надо оптимизировать я полагаю
        """считает сумму всех оценок по каждому критерию
        пока по неправильной формуле +-"""
        grades = self.grades.all()
        for grade in grades:
            for i in range(5):  # должно быть кол-во параметров, а не цифра
                if grade.__dict__['parameter_{}'.format(i)]:
                    self.__dict__['sum_grade_{}'.format(i)] += \
                        grade.__dict__['parameter_{}'.format(i)] * grade.expert.weight

        for i in range(5):  # должно быть кол-во параметров, а не цифра
            self.sum_weight_experts(i)
            self.sum_grade_all += self.__dict__['sum_grade_{}'.format(i)]



    def sum_weight_experts(self, number_parameter):
        """делит на сумму весов экспертов по критерию"""
        grades = self.grades.all()
        sum = 0
        for grade in grades:
            if grade.__dict__['parameter_{}'.format(number_parameter)]:
                sum += grade.expert.weight
        if sum:
            self.__dict__['sum_grade_{}'.format(number_parameter)] /= sum




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
    weight = db.Column(db.Float, default=1.0)
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

    def quantity_grade(self):
        self.quantity += 1

    def __repr__(self):
        return 'Эксперт {}'.format(self.username)


class Grade(db.Model):
    __tablename__ = 'grade'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    expert_id = db.Column(db.String(64), db.ForeignKey('expert.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    parameter_0 = db.Column(db.Integer)
    parameter_1 = db.Column(db.Integer)
    parameter_2 = db.Column(db.Integer)
    parameter_3 = db.Column(db.Integer)
    parameter_4 = db.Column(db.Integer)

    def __repr__(self):
        return 'Оценка для участника номер {}'.format(self.user_id)

    def set_points(self, grades):  # сломается если grades > чем кол-во параметров
        """ устанавливает баллы для критериев """
        for i in range(len(grades)):
            if grades[i] is not None:
                self.__dict__['parameter_{}'.format(i)] = grades[i]


class Viewer(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(64))
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


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(64))
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
