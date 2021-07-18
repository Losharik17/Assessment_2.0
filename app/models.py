from datetime import datetime
from enum import unique
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login
from sqlalchemy import event, DDL


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(128), index=True, unique=True)
    avatar = db.Column(db.BLOB)
    password_hash = db.Column(db.String(128))
    birth_date = db.Column(db.Date)
    team = db.Column(db.String(32))
    grades = db.relationship('Grade', backref='user', lazy='dynamic')
    sum_grade_0 = db.Column(db.Float, default=0)
    sum_grade_1 = db.Column(db.Float, default=0)
    sum_grade_2 = db.Column(db.Float, default=0)
    sum_grade_3 = db.Column(db.Float, default=0)
    sum_grade_4 = db.Column(db.Float, default=0)
    sum_grade_all = db.Column(db.Float, default=0)

    # grade = db.relationship('Expert', secondary='grade', /
    # backref=db.backref('user', lazy='dynamic'), lazy='dynamic')

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
            self.__dict__['sum_grade_{}'.format(i)] /= self.sum_weight_experts(i)
            self.sum_grade_all += self.__dict__['sum_grade_{}'.format(i)]

    def sum_weight_experts(self, number_parameter):
        """делит на сумму весов экспертов по критерию"""
        grades = self.grades.all()
        sum = float(0)
        for grade in grades:
            if grade.__dict__['parameter_{}'.format(number_parameter)] is not None \
                    and grade.__dict__['parameter_{}'.format(number_parameter)] != 0:
                sum += grade.expert.weight
        if sum:
            return sum
        return 1

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
    if int(id) < 10000:
        print(id)
        return User.query.get(int(id))
    if 10000 < int(id) < 11000:
        return Expert.query.get(int(id))
    if 11000 < int(id) < 12000:
        return Admin.query.get(int(id))
    if 12000 < int(id):
        return Viewer.query.get(int(id))


class Expert(UserMixin, db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(128), index=True, unique=True)
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


class Viewer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(128), index=True, unique=True)
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


class Admin(UserMixin, db.Model):
    admin_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(128), index=True, unique=True)
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


event.listen(Expert.__table__, 'after_create',
             DDL("INSERT INTO expert (id) VALUES (10000)")  # аналогично admin_id
             )

event.listen(Admin.__table__, 'after_create',
             DDL("INSERT INTO admin (admin_id) VALUES (11000)")
             )

event.listen(Viewer.__table__, 'after_create',
             DDL("INSERT INTO viewer (id) VALUES (12000)")  # аналогично admin_id
             )


class ParametersName(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(32))
