import json
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app, send_file
from flask_login import current_user, login_required
from app import db
from app.main.forms import EmptyForm, GradeForm, UserForm
from app.models import User, Expert, Grade, Viewer, Admin, Parameter, Project, WaitingUser
from app.main import bp
from app.main.functions import users_in_json, experts_in_json, grades_in_json, \
    waiting_users_in_json, excel_expert, excel_user, to_dict, delete_timer, redirects, compression
from datetime import date, datetime
from werkzeug.utils import secure_filename
import pandas as pd
import os


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/T-Park', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        pass
        # return redirects()

    return render_template('base.html', auth=current_user.is_authenticated)


@bp.route('/download')
@login_required
def dwn():
    """if current_user.id <= 11000:
        return redirects()"""
    return render_template('download.html')


@bp.route('/excel/<project_number>', methods=['GET', 'POST'])
@login_required
def export_excel(project_number):
    """if current_user.id <= 11000:
        return redirects()"""
    data = User.query.all()
    data_list = [to_dict(item) for item in data]
    df1 = pd.DataFrame(data_list)

    parameters = Project.query.filter_by(number=project_number).first().parameters.all()
    i = 0
    for parameter in parameters:
        df1 = df1.rename(columns={"sum_grade_{}".format(i): parameter.name})
        i += 1
    df1 = df1.rename(columns={"region": "Регион", "team": "Команда", "username": "ФИО", "birthday": "Дата рождения",

                              "sum_grade_all": "Итоговая оценка",
                              'project_id': 'ID'})  # надо будет добавить изменение имен через формы
    df1 = df1.fillna('-')
    df1 = df1.loc[df1['project_number'] == int(project_number)]
    df1 = df1.drop(columns=['password_hash', 'id', 'project_number'])

    data = Expert.query.all()
    data_list = [to_dict(item) for item in data]
    df2 = pd.DataFrame(data_list)
    df2 = df2.loc[df2['project_number'] == int(project_number)]
    df2 = df2.drop(columns=['password_hash', 'id', 'project_number', 'quantity'])
    df2.rename(columns={'username': 'ФИО', 'weight': 'Вес', 'project_id': 'ID'}, inplace=True)
    data = Grade.query.all()
    data_list = [to_dict(item) for item in data]
    df3 = pd.DataFrame(data_list)
    df3 = df3.drop(columns=['id'])
    df3.rename(columns={'user_id': 'ID пользователя', 'expert_id': 'ID эксперта',
                        'date': 'Дата выставления оценки', 'comment': 'Комментарий'}, inplace=True)
    i = 0
    for parameter in parameters:
        df3 = df3.rename(columns={"parameter_{}".format(i): parameter.name})
        i += 1

    filename = "/{}.xlsx".format(Project.query.filter_by(number=project_number).first().name)

    writer = pd.ExcelWriter(filename, date_format='dd/mm/yyyy', datetime_format='dd/mm/yyyy hh:mm', engine='xlsxwriter')
    df1.to_excel(writer, sheet_name='Пользователи', index=False, float_format="%.1f")
    workbook = writer.book
    new_format = workbook.add_format({'align': 'center'})
    worksheet = writer.sheets['Пользователи']
    worksheet.set_column('A:L', 19, new_format)
    df2.to_excel(writer, sheet_name='Эксперты', index=False)
    worksheet = writer.sheets['Эксперты']
    worksheet.set_column('A:F', 19, new_format)
    df3.to_excel(writer, sheet_name='Оценки', index=False)
    worksheet = writer.sheets['Оценки']
    worksheet.set_column('A:H', 19, new_format)
    worksheet.set_column('C:C', 24, new_format)
    worksheet.set_column('I:I', 30, new_format)
    writer.save()
    return send_file(filename, as_attachment=True, cache_timeout=0)


# профиль пользователя
@bp.route('/user/<user_id>')
@login_required
def user(user_id):
    user = User.query.filter_by(id=user_id).first()
    """if current_user.id <= 10000 and current_user.id != user.id:
        return redirects()"""
    grades = Grade.query.filter_by(user_id=user_id).order_by(Grade.expert_id).limit(20)
    user = User.query.filter_by(id=user_id).first()
    parameters = Parameter.query.filter_by(project_number=user.project_number).all()
    return render_template('user_grades_table.html', title='Оценки участника',
                           grades=grades, user=user, project_number=user.project_number,
                           ParName=parameters, user_id=user_id)


# ввод номера участника для перехода к выставлению оценки
@bp.route('/expert/<project_number>/<expert_id>', methods=['GET', 'POST'])
@login_required
def expert(project_number, expert_id):
    expert = Expert.query.filter_by(id=expert_id).first()
    """if current_user.id <= 11000 and current_user.id != expert.id:
        return redirects()"""
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(project_number=project_number,
                                    project_id=form.user_id.data).first()
        if user is None:
            flash('Участник с введённым номером не зарегистрирован', 'warning')
            return redirect(url_for('main.expert', project_number=project_number,
                                    expert_id=current_user.id))

        return redirect(url_for('main.expert_grade', project_number=project_number,
                                expert_id=current_user.id, user_id=user.id))
    return render_template('expert.html', form=form, expert=expert)


# таблица личных оценок участника (для админа)
@bp.route('/expert_table/<project_number>/<expert_id>', methods=['GET', 'POST'])
@login_required
def expert_table(project_number, expert_id):
    """if current_user.id <= 11000:
        return redirects()"""
    grades = Grade.query.filter_by(expert_id=expert_id).order_by(Grade.user_id).limit(20)
    expert = Expert.query.filter_by(id=expert_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()
    return render_template('expert_table.html', title='Профиль эксперта',
                           grades=grades, expert=expert, project_number=project_number,
                           ParName=parameters)


# выставление оценки участнику
@bp.route('/expert/<project_number>/<expert_id>/<user_id>', methods=['GET', 'POST'])
@login_required
def expert_grade(project_number, expert_id, user_id):
    """if current_user.id <= 10000:
        return redirects()"""
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

        flash('Оценка сохранена', 'success')
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
    projects = viewer.projects.order_by(Project.start).all()

    return render_template('viewer_main.html', viewer=viewer, projects=projects)


# страница Настройки проектов + доступ к юзерам и экспертам.
@bp.route('/viewer/settings/<viewer_id>/<project_number>', methods=['GET', 'POST'])
@login_required
def viewer_settings(viewer_id, project_number):
    viewer = Viewer.query.filter_by(id=viewer_id).first()
    project = viewer.projects.filter_by(number=project_number).first()
    return render_template('viewer_settings.html', viewer=viewer, project=project)


# таблица всех участников из проекта для наблюдателя
@bp.route('/viewer_table/<project_number>/<viewer_id>', methods=['GET', 'POST'])
@login_required
def viewer_table(project_number, viewer_id):
    """if current_user.id <= 11000:
        return redirects()"""
    viewer = Viewer.query.filter_by(id=viewer_id).first()
    project = Project.query.filter_by(number=project_number).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()
    users_team = User.query.filter_by(project_number=project_number).all()
    teams = ['Все команды']
    regions = ['–']
    for user in users_team:
        if user.team not in teams and user.team is not None:
            teams.append(user.team)
        if user.region not in regions and user.region is not None:
            regions.append(user.region)

    return render_template('viewer_table.html', title='Table', admin=admin, teams=teams,
                           ParName=parameters, project_number=project_number, regions=regions,
                           project=project)


# страница для создания нового проекта
@bp.route('/viewer/create_project/<viewer_id>', methods=['GET', 'POST'])
@login_required
def create_project(viewer_id):
    viewer = Viewer.query.filter_by(id=viewer_id).first()

    if request.method == 'POST':
        # try:
        result = request.form

        project = Project(viewer_id=current_user.id, name=result.get('name'))
        db.session.add(project)
        project = Project.query.all()[-1]

        for i in range(int(result.get('quantity'))):
            db.session.add(Parameter(name=result.get('name{}'.format(i)),
                                     weight=result.get('weight{}'.format(i)),
                                     project_number=project.number))


        os.chdir("app/static/images")
        os.mkdir('{}'.format(project.number))
        os.chdir('{}'.format(project.number))

        logo = request.files['logo']
        logo.save(os.path.join(os.getcwd(), '{}.webp'.format(project.number)))

        users = request.files['users']
        users.save(secure_filename(users.filename.rsplit(".", 1)[0]))
        excel_user(users.filename.rsplit(".", 1)[0], project.number)


        experts = request.files['experts']
        experts.save(secure_filename(experts.filename.rsplit(".", 1)[0]))
        excel_expert(experts.filename.rsplit(".", 1)[0], project.number)

        users_photo = request.files.getlist("users_photo")
        experts_photo = request.files.getlist("experts_photo")

        for photo in users_photo:
            photo.save(os.path.join(os.getcwd(), 'user{}').format(photo.filename))
            compression(100, 150, os.path.join(os.getcwd(), photo.filename))
        for photo in experts_photo:
            photo.save(os.path.join(os.getcwd(), 'expert{}').format(photo.filename))
            compression(100, 150, os.path.join(os.getcwd(), photo.filename))

        db.session.commit()
        os.chdir('../../../../')
        # except:
        #   flash('Что-то пошло не так', 'danger')
        #  db.session.rollback()

        return redirect(url_for('main.viewer', viewer_id=current_user.id))

    return render_template('create_project.html', viewer_id=viewer.id)


# главная страница админа
@bp.route('/admin/<admin_id>', methods=['GET', 'POST'])
@login_required
def admin(admin_id):
    """if current_user.id <= 11000:
        return redirects()"""
    admin = Admin.query.filter_by(id=admin_id).first()
    return render_template('admin.html', admin=admin)


# таблица всех участников из проекта для админа
@bp.route('/admin_users_table/<project_number>/<admin_id>', methods=['GET', 'POST'])
@login_required
def admin_users_table(project_number, admin_id):
    """if current_user.id <= 11000:
        return redirects()"""
    admin = Admin.query.filter_by(id=admin_id).first()
    project = Project.query.filter_by(number=project_number).first()
    parameters = project.parameters.all()
    users_team = User.query.filter_by(project_number=project_number).all()
    teams = ['Все команды']
    regions = ['–']
    for user in users_team:
        if user.team not in teams and user.team is not None:
            teams.append(user.team)
        if user.region not in regions and user.region is not None:
            regions.append(user.region)

    return render_template('admin_users_table.html', title='Участники', admin=admin, teams=teams,
                           ParName=parameters, project_number=project_number, regions=regions,
                           project=project)


# таблица экспертов
@bp.route('/admin_experts_table/<project_number>/<admin_id>', methods=['GET', 'POST'])
@login_required
def admin_experts_table(project_number, admin_id):
    """if current_user.id <= 11000:
        return redirects()"""
    admin = Admin.query.filter_by(id=admin_id).first()
    project = Project.query.filter_by(number=project_number).first()
    parameters = project.parameters.all()

    return render_template('admin_experts_table.html', title='Эксперты', admin=admin,
                           ParName=parameters, project_number=project_number, project=project)


# страница для выдачи ролей
@bp.route('/admin_waiting_users/<admin_id>', methods=['GET', 'POST'])
@login_required
def admin_waiting_users(admin_id):
    waiting_users = WaitingUser.query.limit(15)

    return render_template('admin_waiting_users.html', waiting_users=waiting_users)


# таблица личных оценок участника (для админа)
@bp.route('/user_grades_table_for_admin/<project_number>/<user_id>', methods=['GET', 'POST'])
@login_required
def user_grades_table_for_admin(project_number, user_id):
    """if current_user.id <= 11000:
        return redirects()"""
    grades = Grade.query.filter_by(user_id=user_id).order_by(Grade.expert_id).limit(20)
    user = User.query.filter_by(id=user_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()
    print()
    return render_template('user_grades_table_for_admin.html', title='Оценки участника',
                           grades=grades, user=user, project_number=project_number,
                           ParName=parameters, user_id=user_id, len=len(parameters))


# сортировка таблицы участников или увелечение количества участников в таблице
@bp.route('/sort_users_table', methods=['POST'])
@bp.route('/show_more_users', methods=['POST'])
@login_required
def users_table():
    if int(request.form['lim']) < 10:
        limit = 10
    else:
        limit = int(request.form['lim'])

    users = User.query.filter_by(project_number=request.form['project_number'])
    if request.form['parameter'] != '':
        if request.form['team'] != '' and request.form['team'] != 'Все команды':
            users = users.filter_by(team=request.form['team'])

        if request.form['region'] != '' and request.form['region'] != '–':
            users = users.filter_by(region=request.form['region'])

        if request.form['sort_up'] == 'true':
            if request.form['parameter'] == 'birthday':
                users = users.order_by(User.__dict__[request.form['parameter']].asc()).limit(limit)
            else:
                users = users.order_by(User.__dict__[request.form['parameter']].desc()).limit(limit)
        else:
            if request.form['parameter'] == 'birthday':
                users = users.order_by(User.__dict__[request.form['parameter']].desc()).limit(limit)
            else:
                users = users.order_by(User.__dict__[request.form['parameter']].asc()).limit(limit)
    else:
        users = users.order_by(User.project_id).limit(limit)

    # сортировка по возрасту
    t = date.today()
    new_users = []
    for user in users:
        age = t.year - int(user.birthday.strftime('%Y')) - \
              ((t.month, t.day) <
               (int(user.birthday.strftime('%m')),
                int(user.birthday.strftime('%d'))))
        if int(request.form['min_age']) <= age <= int(request.form['max_age']):
            new_users.append(user)

    return jsonify({'users': users_in_json(new_users)})


@bp.route('/sort_experts_table', methods=['POST'])
@bp.route('/show_more_experts', methods=['POST'])
@login_required
def experts_table():
    if int(request.form['lim']) < 10:
        limit = 10
    else:
        limit = int(request.form['lim'])

    experts = Expert.query.filter_by(project_number=request.form['project_number'])
    if request.form['parameter'] != '':
        if request.form['sort_up'] == 'true':
            experts = experts.order_by(Expert.__dict__[request.form['parameter']].desc()).limit(limit)
        else:
            experts = experts.order_by(Expert.__dict__[request.form['parameter']].asc()).limit(limit)
    else:
        experts = experts.order_by(Expert.project_id).limit(limit)

    return jsonify({'experts': experts_in_json(experts)})


# сортировка личных оценок участника или добавление личных оценок участника в таблицу
@bp.route('/sort_grades_table_for_user', methods=['POST'])
@bp.route('/show_more_grades_for_user', methods=['POST'])
@login_required
def sort_grades_table_for_user():
    if int(request.form['lim']) < 10:
        limit = 10
    else:
        limit = int(request.form['lim'])

    if request.form['parameter'] != '':
        if request.form['sort_up'] == 'true':
            grades = Grade.query.filter_by(user_id=request.form['user_id']).order_by(
                Grade.__dict__[request.form['parameter']].desc()).limit(limit)
        else:
            grades = Grade.query.filter_by(user_id=request.form['user_id']).order_by(
                Grade.__dict__[request.form['parameter']].asc()).limit(limit)
    else:
        grades = Grade.query.order_by(Grade.id).limit(limit)

    return jsonify({'grades': grades_in_json(grades)})


# добавление оценок эксперта в таблицу или сортировка оценок эксперта
@bp.route('/show_more_grades_for_expert', methods=['POST'])
@bp.route('/sort_grades_table_for_expert', methods=['POST'])
@login_required
def show_more_grades_for_expert():
    if int(request.form['lim']) < 10:
        limit = 10
    else:
        limit = int(request.form['lim'])

    if request.form['parameter'] != '':
        if request.form['sort_up'] == 'true':
            grades = Grade.query.filter_by(expert_id=request.form['expert_id']).order_by(
                Grade.__dict__[request.form['parameter']].desc()).limit(limit)
        else:
            grades = Grade.query.filter_by(expert_id=request.form['expert_id']).order_by(
                Grade.__dict__[request.form['parameter']].asc()).limit(limit)
    else:
        grades = Grade.query.order_by(Grade.id).limit(limit)

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
# нужен аргумент Id оценки
@bp.route('/delete_grade', methods=['POST'])
@login_required
def delete_grade():
    grade = Grade.query.get(request.form['id'])

    grade.expert.quantity -= 1
    user = grade.user


    db.session.delete(grade)
    db.session.commit()

    user.sum_grades()
    db.session.commit()

    return jsonify({'result': 'Deleted'})


# назначение роли администратора или наблюдателя
# нужен аргумент Id пользователя
@bp.route('/give_role', methods=['POST'])
@login_required
def give_role():
    if WaitingUser.query.filter_by(id=request.form['id']).first():

        waiting_user = WaitingUser.query.filter_by(id=request.form['id']).first()

        if request.form['role'] == 'Администратор':
            user = Admin(username=waiting_user.username, email=waiting_user.email,
                         password_hash=waiting_user.password_hash)
        elif request.form['role'] == 'Заказчик':
            user = Viewer(username=waiting_user.username, email=waiting_user.email,
                          password_hash=waiting_user.password_hash)
        elif request.form['role'] == 'Удалить':
            db.session.delete(waiting_user)
            db.session.commit()
            return jsonify({'result': 'deleted'})
        else:
            return jsonify({'result': 'error'})

        expert = Expert(username=waiting_user.username, email=waiting_user.email,
                        password_hash=waiting_user.password_hash)

        db.session.add(user)
        db.session.add(expert)
        db.session.delete(waiting_user)
        db.session.commit()

        return jsonify({'result': 'success'})

    return jsonify({'result': 'User not found'})


# удаление пользователя с любым уровенем доступа
# нужны аргументы Role и Id
@bp.route('/delete_user', methods=['POST'])
@login_required
def delete_user():
    role = request.form['role'].lower()

    if role == 'user':
        user = User.query.filter_by(id=request.form['id']).first()
    elif role == 'expert':
        user = Expert.query.filter_by(id=request.form['id']).first()
    elif role == 'waiting_user':
        user = WaitingUser.query.filter_by(id=request.form['id']).first()
    elif role == 'viewer':
        user = Viewer.query.filter_by(id=request.form['id']).first()
    elif role == 'admin':
        user = Admin.query.filter_by(id=request.form['id']).first()
    else:
        return jsonify({'result': 'User not found'})

    db.session.delete(user)
    db.session.commit()
    return jsonify({'result': 'success'})


# увелечение количества отображаемых пользователей в таблице раздачи ролей
@bp.route('/show_more_waiting_users', methods=['POST'])
@login_required
def show_more_waiting_users():
    if request.form['parameter'] != '':
        if request.form['sort_up'] == 'true':

            waiting_users = WaitingUser.query \
                .order_by(WaitingUser.__dict__[request.form['parameter']].desc()) \
                .limit(request.form['lim'])

        else:
            waiting_users = WaitingUser.query \
                .order_by(WaitingUser.__dict__[request.form['parameter']].asc()) \
                .limit(request.form['lim'])
    else:
        waiting_users = WaitingUser.query \
            .order_by(WaitingUser.project_id).limit(request.form['lim'])

    return jsonify({'waiting_users': waiting_users_in_json(waiting_users)})


# сортировка таблицы зарегистрированных пользователей
@bp.route('/sort_waiting_users', methods=['POST'])
@login_required
def sort_waiting_users():
    if request.form['sort_up'] == 'true':
        waiting_users = WaitingUser.query \
            .order_by(WaitingUser.__dict__[request.form['parameter']].desc()) \
            .limit(request.form['lim'])
    else:
        waiting_users = WaitingUser.query \
            .order_by(WaitingUser.__dict__[request.form['parameter']].asc()) \
            .limit(request.form['lim'])

    return jsonify({'waiting_users': waiting_users_in_json(waiting_users)})


@bp.route('/save_expert_data', methods=['POST'])
@login_required
def save_expert_data():
    data = list(json.loads(request.form['data']))
    expert = Expert.query.filter_by(id=request.form['expert_id']).first()

    if getattr(expert, 'username') != data[0]:
        setattr(expert, 'username', data[0])

    if getattr(expert, 'weight') != data[1]:
        setattr(expert, 'weight', data[1])

    db.session.commit()

    return jsonify({'result': 'successfully'})


@bp.route('/save_user_data', methods=['POST'])
@login_required
def save_user_data():
    data = list(json.loads(request.form['data']))
    user = User.query.filter_by(id=request.form['user_id']).first()

    if getattr(user, 'username') != data[0]:
        setattr(user, 'username', data[0])

    if getattr(user, 'team') != data[2].title():
        setattr(user, 'team', data[2].title())

    if getattr(user, 'region') != data[3]:
        setattr(user, 'region', data[3])

    x = data[1].split('-')
    x.reverse()
    setattr(user, 'birthday', datetime.strptime(''.join(x), '%d%m%Y'))

    db.session.commit()

    return jsonify({'result': 'successfully'})
