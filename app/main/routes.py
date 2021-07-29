import json
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app, send_file
from flask_login import current_user, login_required
from app import db
from app.main.forms import EmptyForm, GradeForm, UserForm, TableForm
from app.models import User, Expert, Grade, Viewer, Admin, ParametersName
from app.main import bp
from app.main.functions import users_in_json, grades_in_json, excell, to_dict
import pandas as pd
from werkzeug.utils import secure_filename


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/T-Park', methods=['GET', 'POST'])
def index():
    return render_template('base.html', auth=current_user.is_authenticated)


@bp.route('/download')
def dwn():
    return render_template('download.html')


@bp.route('/excel', methods=['GET', 'POST'])
def exportexcel():
    data = User.query.all()
    data_list = [to_dict(item) for item in data]
    df1 = pd.DataFrame(data_list)
    df1 = df1.drop(columns=['password_hash'])
    data = Expert.query.all()
    data_list = [to_dict(item) for item in data]
    df2 = pd.DataFrame(data_list)
    df2 = df2.drop(columns=['password_hash'])
    data = Grade.query.all()
    data_list = [to_dict(item) for item in data]
    df3 = pd.DataFrame(data_list)
    df3 = df3.drop(columns=['id'])
    filename = "/Отчёт.xlsx"

    writer = pd.ExcelWriter(filename)
    df1.to_excel(writer, sheet_name='Пользователи', index=False)
    df2.to_excel(writer, sheet_name='Эксперты', index=False)
    df3.to_excel(writer, sheet_name='Оценки', index=False)
    writer.save()
    return send_file(filename, as_attachment=True, cache_timeout=0)


@bp.route('/upload')
def upload_file1():
    return render_template('upload.html')


@bp.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename.rsplit( ".", 1 )[ 0 ]))
        excell(f.filename.rsplit( ".", 1 )[ 0 ])
        return redirect(url_for('main.expert'))
    return render_template('upload.html')


@bp.route('/user/<user_id>')
@login_required
def user(user_id):
    user = User.query.filter_by(id=user_id).first()
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
            return redirect(url_for('main.expert', expert_id=current_user.id))
        return redirect(url_for('main.expert_grade', expert_id=current_user.id, user_id=user.id))
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
    user = User.query.filter_by(id=user_id).first()
    parameters_name = ParametersName.query.all()
    form = GradeForm()
    return render_template('user_grades_table.html', title='Rating', grades=grades, user=user,
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


@bp.route('/user_popup', methods=['POST'])
@login_required
def user_popup():
    user = User.query.filter_by(id=request.form['user_id']).first()
    user = users_in_json([user])
    return jsonify({'result': 'Deleted'})
