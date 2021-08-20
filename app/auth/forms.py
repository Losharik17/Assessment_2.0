from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Regexp, Length
from app.models import User
from wtforms.fields.html5 import DateField


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email("Некорректный email")])
    password = PasswordField('Пароль', validators=[DataRequired(message="Неверный пароль")])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    avatar = FileField('Фото')
    phone_number = StringField('Номер Телефона')
    email = StringField('Email', validators=[DataRequired(), Email("Некорректный email")])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Данная почта уже используется другим пользователем.')

    def validate_phone_number(self, phone_number):
        user = User.query.filter_by(phone=phone_number.data).first()
        if user is not None:
            raise ValidationError('Данный номер уже используется другим пользователем.')

        for i in enumerate(phone_number):
            if not i.isdigit():
                raise ValidationError('Неверно введен телефонный номер')
            elif i[0] > 10:
                raise ValidationError('Номер телефона слишком длинный')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email("Некорректный email")])
    submit = SubmitField('Сбросить пароль')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(),
                                                              EqualTo('password')])
    submit = SubmitField('Установить пароль')
