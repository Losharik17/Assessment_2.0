from flask_wtf import FlaskForm
from sqlalchemy import Integer
from wtforms import StringField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import ValidationError, DataRequired, Length

from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    about_me = TextAreaField('Обо мне',
                             validators=[Length(min=0, max=140)])
    submit = SubmitField('Сохранить')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Пожалуйста используйте другое имя.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Принять')


class GradeForm(FlaskForm):
    parameter_0 = IntegerField('{}'.format('')) # подтянуть из БД название параметра
    parameter_1 = IntegerField('{}'.format(''))
    parameter_2 = IntegerField('{}'.format(''))
    parameter_3 = IntegerField('{}'.format(''))
    parameter_4 = IntegerField('{}'.format(''))

    submit = SubmitField('Принять')


class UserForm(FlaskForm):
    user_id = IntegerField('Номер участника')
    submit = SubmitField('')


class TableForm(FlaskForm):
    pass
