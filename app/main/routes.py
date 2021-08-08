import json
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app, send_file
from flask_login import current_user, login_required
from app import db
from app.main.forms import EmptyForm, GradeForm, UserForm
from app.models import User, Expert, Grade, Viewer, Admin, Parameter, Project
from app.main import bp
from app.main.functions import users_in_json, grades_in_json, excel, to_dict
from werkzeug.utils import secure_filename
import os


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/T-Park', methods=['GET', 'POST'])
def index():
    return render_template('base.html', auth=current_user.is_authenticated)


@bp.route('/download')
def dwn():
    return render_template('download.html')


@bp.route('/excel', methods=['GET', 'POST'])
def export_excel():
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
    filename = "/Name.xlsx"

    writer = pd.ExcelWriter(filename)
    df1.to_excel(writer, sheet_name='Пользователи', index=False)
    df2.to_excel(writer, sheet_name='Эксперты', index=False)
    df3.to_excel(writer, sheet_name='Оценки', index=False)
    writer.save()
    return send_file(filename, as_attachment=True, cache_timeout=0)


@bp.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(secure_filename(f.filename.rsplit(".", 1)[0]))
        excel(f.filename.rsplit(".", 1)[0])
        return redirect(url_for('main.index'))
    return render_template('upload.html')


# профиль пользователя
@bp.route('/user/<user_id>')
@login_required
def user(user_id):
    user = User.query.filter_by(id=user_id).first()
    return render_template('user.html', user=user)


# ввод номера участника для перехода к выставлению оценки
@bp.route('/expert/<project_number>/<expert_id>', methods=['GET', 'POST'])
@login_required
def expert(project_number, expert_id):
    expert = Expert.query.filter_by(id=expert_id).first()
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(project_number=project_number,
                                    project_id=form.user_id.data).first()
        if user is None:
            flash('Участник с введённым номером не зарегистрирован')
            return redirect(url_for('main.expert', project_number=project_number,
                                    expert_id=current_user.id))

        return redirect(url_for('main.expert_grade', project_number=project_number,
                                expert_id=current_user.id, user_id=user.id))
    return render_template('expert.html', form=form, expert=expert)


# выставление оценки участнику
@bp.route('/expert/<project_number>/<expert_id>/<user_id>', methods=['GET', 'POST'])
@login_required
def expert_grade(project_number, expert_id, user_id):
    form = GradeForm()
    if form.validate_on_submit():
        if 11000 < current_user.id <= 12000:
            expert = Admin.query.filter_by(id=current_user.id).first()
        elif 12000 < current_user.id:
            expert = Viewer.query.filter_by(id=current_user.id).first()
        else:
            expert = Expert.query.filter_by(id=current_user.id).first()
        grade = Grade(user_id=user_id, expert_id=expert.id, comment=form.comment.data)
        grade_parameters = [form.parameter_0.data, form.parameter_1.data, form.parameter_2.data,
                            form.parameter_3.data, form.parameter_4.data]
        grade.set_points(grade_parameters)
        db.session.add(grade)
        db.session.commit()
        grade.user.sum_grades()
        expert.quantity_grade()
        db.session.commit()

        flash('Оценка сохранена')
        return redirect(url_for('main.expert', project_number=project_number,
                                expert_id=current_user.id))

    user = User.query.filter_by(id=user_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()

    if (user.project_number == Expert.query.filter_by(
            id=current_user.id).first().project_number):
        pass
    return render_template('expert_grade.html', form=form, expert_id=current_user.id,
                           user=user, parameters=parameters, project_number=project_number)


# главня страница наблюдателя
@bp.route('/viewer/<viewer_id>', methods=['GET', 'POST'])
@login_required
def viewer(viewer_id):
    viewer = Viewer.query.filter_by(id=viewer_id).first()
    return render_template('viewer.html', viever=viewer)


# страница для создания нового проекта
@bp.route('/viewer/create_project/<viewer_id>', methods=['GET', 'POST'])
@login_required
def create_project(viewer_id):
    viewer = Viewer.query.filter_by(id=current_user.id).first()

    if request.method == 'POST':
        project = Project(viewer_id=current_user.id)
        result = request.form

        for i in range(result.get('quantity')):
            Parameter(name=result.get('name{}'.format(i)),
                      weight=result.get('weight{}'.format(i)),
                      project_number=project.number)
            db.session.commit()

        logo = request.files['logo']
        path = os.path.join('/app/static/images')
        logo.save(os.path.join(path, '{}.webp'.format(project.number)))

        users = request.files['users']
        users.save(secure_filename(users.filename.rsplit(".", 1)[0]))
        excel(users.filename.rsplit(".", 1)[0])

        experts = request.files['experts']
        experts.save(secure_filename(experts.filename.rsplit(".", 1)[0]))
        excel(experts.filename.rsplit(".", 1)[0])

        db.session.commit()  # наверное не нужна

        return redirect(url_for('main.project', project_number=project.number,
                                viewer_id=current_user.id))

    return render_template('create_project.html', viewer=viewer)


# главная страница админа
@bp.route('/admin/<admin_id>', methods=['GET', 'POST'])
@login_required
def admin(admin_id):
    admin = Admin.query.filter_by(id=admin_id).first()
    return render_template('admin.html', admin=admin)


# таблица всех участников из проекта
@bp.route('/admin_table/<project_number>/<admin_id>', methods=['GET', 'POST'])
@login_required
def admin_table(project_number, admin_id):
    admin = Admin.query.filter_by(id=admin_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()
    users = User.query.filter_by(project_number=project_number).order_by(User.id).limit(5)
    return render_template('admin_table.html', title='Table', admin=admin,
                           users=users, ParName=parameters, project_number=project_number)


# таблица личных оценок участника (для админа)
@bp.route('/user_grades_table/<project_number>/<user_id>', methods=['GET', 'POST'])
@login_required
def user_grades_table(project_number, user_id):
    grades = Grade.query.filter_by(user_id=user_id).order_by(Grade.expert_id).limit(5)
    user = User.query.filter_by(id=user_id).first()
    parameters = Parameter.query.all()
    return render_template('user_grades_table.html', title='Rating', grades=grades, user=user,
                           project_number=project_number, ParName=parameters,
                           user_id=user_id)


# сортировка таблицы участников
@bp.route('/sort_users_table', methods=['POST'])
@login_required
def sort_users_table():
    if request.form['sort_up'] == 'true':
        users = User.query.filter_by(project_number=request.form['project_number'])\
            .order_by(User.__dict__[request.form['parameter']].desc())\
            .limit(request.form['lim'])
    else:
        users = User.query.filter_by(project_number=request.form['project_number'])\
            .order_by(User.__dict__[request.form['parameter']].asc())\
            .limit(request.form['lim'])

    return jsonify({'users': users_in_json(users)})


# добавление участников в таблицу
@bp.route('/show_more_users', methods=['POST'])
@login_required
def show_more_users():
    if request.form['parameter'] != '':
        if request.form['sort_up'] == 'true':
            users = User.query.filter_by(project_number=request.form['project_number'])\
                .order_by(User.__dict__[request.form['parameter']].desc())\
                .limit(request.form['lim'])
        else:
            users = User.query.filter_by(project_number=request.form['project_number'])\
                .order_by(User.__dict__[request.form['parameter']].asc())\
                .limit(request.form['lim'])
    else:
        users = User.query.filter_by(project_number=request.form['project_number'])\
            .order_by(User.id).limit(request.form['lim'])

    return jsonify({'users': users_in_json(users)})


# сортировка личных оценок участника
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


# добавление личных оценок участника в таблицу
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


# сохранение изменений оценки
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


# удаление оценки
@bp.route('/delete_grade', methods=['POST'])
@login_required
def delete_grade():
    grade = Grade.query.get(request.form['id'])
    user = User.query.get(grade.user.id)
    db.session.delete(grade)
    db.session.commit()
    user.sum_grades()
    db.session.commit()

    return jsonify({'result': 'Deleted'})
