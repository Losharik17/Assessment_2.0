from flask_wtf import FlaskForm
from sqlalchemy import Integer
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, RadioField, FileField
from wtforms.validators import ValidationError, DataRequired, Length

from app.models import User


class EmptyForm(FlaskForm):
    submit = SubmitField('Принять')


class GradeForm(FlaskForm):
    parameter_0 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, '')])
    parameter_1 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, '')])
    parameter_2 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, '')])
    parameter_3 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, '')])
    parameter_4 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, '')])
    parameter_5 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, '')])
    parameter_6 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, '')])
    parameter_7 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, '')])
    parameter_8 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, '')])
    parameter_9 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, '')])
    comment = TextAreaField('Комментарий к оценке', validators=[Length(max=200)])
    submit = SubmitField('Сохранить')


class UserForm(FlaskForm):
    user_id = IntegerField('Номер участника')
    submit = SubmitField('Продолжить')


class UserRegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    birthday = StringField('Дата Рождения')
    team = StringField('Команда')
    region = StringField('Регион')
    avatar = FileField('Фото')
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class ExpertRegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    avatar = FileField('Фото')
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
