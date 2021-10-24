from datetime import datetime
from enum import unique
from hashlib import md5
from time import time
from flask import current_app, request
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login
from sqlalchemy import event, DDL


class User(UserMixin, db.Model):
    project_id = db.Column(db.Integer)  # id в данном проете
    username = db.Column(db.String(64))
    email = db.Column(db.String(128), index=True)
    birthday = db.Column(db.Date)
    team = db.Column(db.String(32), default='–')  # команда, класс иди что-то подобное
    region = db.Column(db.String(64), default='–')  # локация, регион или что-то подобное
    project_number = db.Column(db.Integer)  # номер проекта к которму относится
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)  # общий id
    password_hash = db.Column(db.String(128))
    photo = db.Column(db.String(1024))
    grades = db.relationship('Grade', backref='user', lazy='dynamic')
    sum_grade_0 = db.Column(db.Float, default=0)
    sum_grade_1 = db.Column(db.Float, default=0)
    sum_grade_2 = db.Column(db.Float, default=0)
    sum_grade_3 = db.Column(db.Float, default=0)
    sum_grade_4 = db.Column(db.Float, default=0)
    sum_grade_5 = db.Column(db.Float, default=0)
    sum_grade_6 = db.Column(db.Float, default=0)
    sum_grade_7 = db.Column(db.Float, default=0)
    sum_grade_8 = db.Column(db.Float, default=0)
    sum_grade_9 = db.Column(db.Float, default=0)
    sum_grade_all = db.Column(db.Float, default=0)

    def __repr__(self):
        return '<Пользователь {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = password

    def check_password(self, password):
        return self.password_hash == password

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    def sum_grades(self):
        """считает сумму всех оценок по каждому критерию
        пока по неправильной формуле +-"""

        grades = self.grades.all()
        parameters = Parameter.query.filter_by(project_number=self.project_number).all()
        setattr(self, 'sum_grade_all', float(0))
        for i in range(len(parameters)):
            setattr(self, 'sum_grade_{}'.format(i), 0)

        for grade in grades:
            for i in range(len(parameters)):  # должно быть кол-во параметров, а не цифра
                if grade.__dict__['parameter_{}'.format(i)]:
                    setattr(self, 'sum_grade_{}'.format(i),
                            (float(self.__dict__['sum_grade_{}'.format(i)]) +
                             grade.__dict__['parameter_{}'.format(i)] * grade.expert.weight))

        for i in range(len(parameters)):  # должно быть кол-во параметров, а не цифра
            setattr(self, 'sum_grade_{}'.format(i),
                    self.__dict__['sum_grade_{}'.format(i)] / self.sum_weight_experts(i))
            if len(parameters) > i:  # нужен тест
                self.sum_grade_all += self.__dict__['sum_grade_{}'.format(i)] * parameters[i].weight
        db.session.commit()

    def sum_weight_parameters(self, parameters):
        sum = 0
        i = 0
        for parameter in parameters:
            if self.__dict__['sum_grade_{}'.format(i)] != 0:
                sum += parameter.weight
            i += 1
        if sum:
            return sum
        return 1

    def sum_weight_experts(self, number_parameter):
        """делит на сумму весов экспертов по критерию"""
        grades = self.grades.all()
        sum = float(0)
        for grade in grades:
            if getattr(grade, 'parameter_{}'.format(number_parameter)) is not None \
                    and getattr(grade, 'parameter_{}'.format(number_parameter)) != 0:
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
    if int(id) <= 1000000:
        return User.query.get(int(id))
    if 1000000 < int(id) <= 1100000:
        return Expert.query.get(int(id))
    if 1100000 < int(id) <= 1200000:
        return Viewer.query.get(int(id))
    if 1200000 < int(id):
        return Admin.query.get(int(id))


class Expert(UserMixin, db.Model):
    project_id = db.Column(db.Integer)
    username = db.Column(db.String(64))
    email = db.Column(db.String(128), index=True)
    weight = db.Column(db.Float, default=1.0)
    photo = db.Column(db.String(1024))
    project_number = db.Column(db.Integer)
    id = db.Column(db.Integer, unique=True, primary_key=True)
    grades = db.relationship('Grade', backref='expert', lazy='dynamic')
    quantity = db.Column(db.Integer, default=0)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = password

    def check_password(self, password):
        return self.password_hash == password

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return Expert.query.get(id)

    def quantity_grade(self):
        self.quantity += 1

    def __repr__(self):
        return 'Эксперт {}'.format(self.username)


class Grade(db.Model):
    __tablename__ = 'grade'

    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    expert_id = db.Column(db.String(64), db.ForeignKey('expert.id'))
    date = db.Column(db.DateTime, default=datetime.now())
    parameter_0 = db.Column(db.Integer)
    parameter_1 = db.Column(db.Integer)
    parameter_2 = db.Column(db.Integer)
    parameter_3 = db.Column(db.Integer)
    parameter_4 = db.Column(db.Integer)
    parameter_5 = db.Column(db.Integer)
    parameter_6 = db.Column(db.Integer)
    parameter_7 = db.Column(db.Integer)
    parameter_8 = db.Column(db.Integer)
    parameter_9 = db.Column(db.Integer)
    comment = db.Column(db.Text(200))

    def __repr__(self):
        return 'Оценка для участника номер {}'.format(self.user_id)

    def set_points(self, grades):  # сломается если grades > чем кол-во параметров
        """ устанавливает баллы для критериев """
        for i in range(len(grades)):
            if grades[i] is not None:
                setattr(self, 'parameter_{}'.format(i), grades[i])


class Viewer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(64))
    organization = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, unique=True)
    phone_number = db.Column(db.String(16))
    password_hash = db.Column(db.String(128))
    projects = db.relationship('ViewerProjects', backref='viewer', lazy='dynamic')
    expert_id = db.Column(db.Integer)

    def set_password(self, password):
        self.password_hash = password

    def check_password(self, password):
        return self.password_hash == password

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
        return Viewer.query.get(id)


class ViewerProjects(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    viewer_id = db.Column(db.Integer, db.ForeignKey('viewer.id'))
    project_number = db.Column(db.Integer, db.ForeignKey('project.number'))


class Project(db.Model):
    number = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(32))
    start = db.Column(db.Date)
    end = db.Column(db.Date)
    parameters = db.relationship('Parameter', backref='project', lazy='dynamic')
    viewers = db.relationship('ViewerProjects', backref='project', lazy='dynamic')


class Parameter(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    name = db.Column(db.String(32))
    weight = db.Column(db.Float, default=1.0)
    project_number = db.Column(db.Integer, db.ForeignKey('project.number'))


# содержит данные о только что зарегистрированных пользователях
# после определения роли пользователь удаляется из данной таблицы
class WaitingUser(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(64))
    organization = db.Column(db.String(128))
    email = db.Column(db.String(128), index=True, unique=True)
    phone_number = db.Column(db.String(16))
    registration_date = db.Column(db.DateTime, default=datetime.now())
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = password

    def __repr__(self):
        return 'Пользователь {}'.format(self.id)


class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(128), index=True, unique=True)
    phone_number = db.Column(db.String(16))
    password_hash = db.Column(db.String(128))
    expert_id = db.Column(db.Integer)
    viewer_id = db.Column(db.Integer)

    def set_password(self, password):
        self.password_hash = password

    def check_password(self, password):
        return self.password_hash == password

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
        return Admin.query.get(id)


event.listen(Expert.__table__, 'after_create',
             DDL("INSERT INTO expert (id) VALUES (1000000)")
             )

event.listen(Viewer.__table__, 'after_create',
             DDL("INSERT INTO viewer (id) VALUES (1100000)")
             )

event.listen(Admin.__table__, 'after_create',
             DDL("INSERT INTO admin (id) VALUES (1200000)")
             )
