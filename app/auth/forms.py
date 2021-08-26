from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length
from app.models import User, Admin, Viewer, WaitingUser
from wtforms.fields.html5 import DateField


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email("Некорректный email")])
    password = PasswordField('Пароль', validators=[DataRequired(message="Неверный пароль")])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    organization = StringField('Название Организации')
    #avatar = FileField('Фото')
    phone_number = StringField('Номер Телефона')
    email = StringField('Email', validators=[DataRequired(), Email("Некорректный email")])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        users = []
        users.append(Admin.query.filter_by(email=email.data).first())
        users.append(Viewer.query.filter_by(email=email.data).first())
        users.append(WaitingUser.query.filter_by(email=email.data).first())
        for user in users:
            if user is not None:
                raise ValidationError('Данная почта уже используется другим пользователем.')

    #def validate_phone_number(self, phone_number):
    #    users = []
    #    users.append(Admin.query.filter_by(phone_number=phone_number.data).first())
    #    users.append(Viewer.query.filter_by(phone_number=phone_number.data).first())
    #    users.append(WaitingUser.query.filter_by(phone_number=phone_number.data).first())

    #    for user in users:
    #        if user is not None:
    #            raise ValidationError('Данный номер уже используется другим пользователем.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email("Некорректный email")])
    submit = SubmitField('Сбросить пароль')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(),
                                                              EqualTo('password')])
    submit = SubmitField('Установить пароль')
