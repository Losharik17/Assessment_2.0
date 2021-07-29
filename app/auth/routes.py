from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Expert, Admin, Viewer
from app.auth.email import send_password_reset_email
import os
from werkzeug.utils import secure_filename


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # при вводе несущкствующего email ничего не происходит, не высвечиваются ошибки
    if current_user.is_authenticated:
        return redirect(url_for('main.index', user=current_user))
    form = LoginForm()
    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            user = Expert.query.filter_by(email=form.email.data).first()
            if not user:
                user = Admin.query.filter_by(email=form.email.data).first()
                if not user:
                    user = Viewer.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неправильный пароль или email')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index', user=None))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index', user=current_user))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data) is None or \
                Expert.query.filter_by(email=form.email.data) is None or \
                Admin.query.filter_by(email=form.email.data) is None or \
                Viewer.query.filter_by(email=form.email.data) is None:
            flash('Данная почта уже используется одним из пользователей<br>'
                  'Пожалуйста изпользуйте другой email адрес')
            return redirect(url_for('auth.register'))

        path = os.path.join('/WEB/T-Park/app/static/images')
        form.avatar.data.save(os.path.join(path, '{}.webp'.format(form.email.data)))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Проверьте вашу почту и следуйте дальнейшим инструкциям')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Сбросить пароль', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Ваш пароль был изменён')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
