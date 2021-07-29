from flask_wtf import FlaskForm
from sqlalchemy import Integer
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, RadioField
from wtforms.validators import ValidationError, DataRequired, Length

from app.models import User


class EmptyForm(FlaskForm):
    submit = SubmitField('Принять')


class GradeForm(FlaskForm):
    parameter_0 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, 'Ничего')])
    parameter_1 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, 'Ничего')])
    parameter_2 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, 'Ничего')])
    parameter_3 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, 'Ничего')])
    parameter_4 = RadioField('{}'.format(''), default=0,
                             choices=[(-1, '-1'), (1, '1'), (2, '2'), (3, '3'), (0, 'Ничего')])

    submit = SubmitField('Выставить оценки')


class UserForm(FlaskForm):
    user_id = IntegerField('Номер участника')
    submit = SubmitField('Продолжить')


class TableForm(FlaskForm):
    pass
