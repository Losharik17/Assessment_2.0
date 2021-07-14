from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, \
    jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, EmptyForm, GradeForm
from app.models import User, Expert, Grade
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/T-Park', methods=['GET', 'POST'])
@login_required
def index():
    return render_template()


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@bp.route('/expert/<expert_id>', methods=['GET', 'POST'])
@login_required
def expert(expert_id):
    expert = Expert.query.filter_by(expert_id=expert_id).first_or_404()
    form = GradeForm()
    if form.validate_on_submit():
        grade = Grade(user_id=form.user_id.data, expert_id=current_user.id.data)
        grade.ser_points(form.parametrs.data) # функция не написана
        ...
        db.session.add(form)
        db.session.commit()
    return render_template('expert.html', expert=expert, form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
