import json
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, EmptyForm, GradeForm, UserForm, TableForm
from app.models import User, Expert, Grade, Viewer, Admin, ParametersName
from app.main import bp
from app.main.smth_in_json import users_in_json, grades_in_json


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/T-Park', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('base.html')


@bp.route('/user/<id>')
@login_required
def user(id):
    user = User.query.filter_by(username=id).first()
    return render_template('user.html', user=user)


@bp.route('/expert/<expert_id>', methods=['GET', 'POST'])
@login_required
def expert(expert_id):
    expert = Expert.query.filter_by(id=expert_id).first()
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=form.user_id.data).first()
        if user is None:
            flash('None User')
            return redirect(url_for('main.expert'))
        return redirect(url_for('main.expert_grade', expert_id=expert.id, user_id=user.id))
    return render_template('expert.html', form=form, expert=expert)


@bp.route('/expert/<expert_id>/<user_id>', methods=['GET', 'POST'])
@login_required
def expert_grade(expert_id, user_id):
    form = GradeForm()
    parameters = ParametersName.query.all()
    if form.validate_on_submit():
        expert = Expert.query.filter_by(id=expert_id).first()
        grade = Grade(user_id=user_id, expert_id=current_user.id)
        parameters = [form.parameter_0.data, form.parameter_1.data, form.parameter_2.data, form.parameter_3.data,
                      form.parameter_4.data]
        grade.set_points(parameters)
        db.session.add(grade)
        db.session.commit()
        grade.user.sum_grades()
        expert.quantity_grade()
        db.session.commit()

        flash('Text')
        return redirect(url_for('main.expert', expert_id=current_user.id))

    return render_template('expert_grade.html', form=form,
                           user=user, parameters=parameters)


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
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/viewer/<viewer_id>', methods=['GET', 'POST'])
@login_required
def viewer(viewer_id):
    viewer = Viewer.query.filter_by(viewer_id=viewer_id).first()
    return render_template('viewer.html', viever=viewer)


@bp.route('/admin/<admin_id>', methods=['GET', 'POST'])
@login_required
def admin(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    return render_template('admin.html', admin=admin)


@bp.route('/admin_table/<admin_id>', methods=['GET', 'POST'])
@login_required
def admin_table(admin_id):
    admin = Admin.query.filter_by(admin_id=admin_id).first()
    parameters_name = ParametersName.query.all()
    users = User.query.order_by(User.id).limit(5)
    return render_template('admin_table.html', title='Rating', admin=admin,
                           users=users, ParName=parameters_name)


@bp.route('/user_grades_table/<user_id>', methods=['GET', 'POST'])
@login_required
def user_grades_table(user_id):
    grades = Grade.query.filter_by(user_id=user_id).order_by(Grade.expert_id).limit(5)
    parameters_name = ParametersName.query.all()
    form = GradeForm()
    return render_template('user_grades_table.html', title='Rating', grades=grades,
                           ParName=parameters_name, user_id=user_id, form=form)


@bp.route('/sort_users_table', methods=['POST'])
@login_required
def sort_users_table():
    if request.form['sort_up'] == 'true':
        users = User.query.order_by(User.__dict__[request.form['parameter']].desc()).limit(request.form['lim'])
    else:
        users = User.query.order_by(User.__dict__[request.form['parameter']].asc()).limit(request.form['lim'])

    return jsonify({'users': users_in_json(users)})


@bp.route('/show_more_users', methods=['POST'])
@login_required
def show_more_users():
    if request.form['parameter'] != '':
        if request.form['sort_up'] == 'true':
            users = User.query.order_by(User.__dict__[request.form['parameter']].desc()).limit(request.form['lim'])
        else:
            users = User.query.order_by(User.__dict__[request.form['parameter']].asc()).limit(request.form['lim'])
    else:
        users = User.query.order_by(User.id).limit(request.form['lim'])

    return jsonify({'users': users_in_json(users)})


@bp.route('/sort_grades_table', methods=['POST'])
@login_required
def sort_grades_table():
    if request.form['sort_up'] == 'true':
        grades = Grade.query.filter_by(user_id=request.form['user_id']).order_by(
            Grade.__dict__[request.form['parameter']].desc()).limit(request.form['lim'])
    else:
        grades = Grade.query.filter_by(user_id=request.form['user_id']).order_by(
            Grade.__dict__[request.form['parameter']].asc()).limit(request.form['lim'])

    return jsonify({'grades': grades_in_json(grades)})


@bp.route('/show_more_grades', methods=['POST'])
@login_required
def show_more_grades():
    if request.form['parameter'] != '':
        if request.form['sort_up'] == 'true':
            grades = Grade.query.filter_by(user_id=request.form['user_id']).order_by(
                Grade.__dict__[request.form['parameter']].desc()).limit(request.form['lim'])
        else:
            grades = Grade.query.filter_by(user_id=request.form['user_id']).order_by(
                Grade.__dict__[request.form['parameter']].asc()).limit(request.form['lim'])
    else:
        grades = Grade.query.order_by(Grade.id).limit(request.form['lim'])

    return jsonify({'grades': grades_in_json(grades)})


@bp.route('/save_grade', methods=['POST'])
@login_required
def save_grade():
    grades = list(json.loads(request.form['grades']))
    grade = Grade.query.filter_by(id=request.form['grade_id']).first()
    usl = False

    for i in range(len(grades)):
        if getattr(grade, 'parameter_{}'.format(i)) != grades[i]:
            setattr(grade, 'parameter_{}'.format(i), grades[i])
            usl = True
    db.session.commit()

    if usl:
        grade.user.sum_grades()
        db.session.commit()
        return jsonify({'result': 'successfully'})

    return jsonify({'result': 'nothing'})


@bp.route('/delete_grade', methods=['POST'])
@login_required
def delete_grade():
    grade = Grade.query.get(request.form['id'])
    db.session.delete(grade)
    db.session.commit()

    return jsonify({'result': 'Deleted'})
