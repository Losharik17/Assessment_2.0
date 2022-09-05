import datetime
import json
import sqlalchemy
from app.email import send_mail_proj, async_mail_proj, mail_test
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app, send_file, g
from flask_login import current_user, login_required
from flask_principal import Principal, Permission, RoleNeed, Identity, identity_changed, identity_loaded, \
    AnonymousIdentity, ActionNeed
from app import db, principal
from app.main.forms import GradeForm, UserForm
from app.models import User, Expert, Grade, Viewer, Admin, Parameter, Project, WaitingUser, ViewerProjects
from app.main import bp
from app.main.functions import users_in_json, experts_in_json, grades_in_json, \
    waiting_users_in_json, viewers_in_json, \
    excel_expert, excel_user, to_dict, redirects, compression, \
    password_generator, project_settings, excel_saver, excel_letter
from app.auth.email import send_role_update, send_role_refuse, send_password_mail
import pandas as pd
from app.main.secure_filename_2 import secure_filename_2
import os
from datetime import date, datetime
import shutil
from sqlalchemy import create_engine

engine = create_engine("sqlite:///T_Park.db")
sql_null = sqlalchemy.null()

# Needs
be_viewer = RoleNeed('viewers')
be_expert = RoleNeed('experts')
be_admin = RoleNeed('administrator')
be_user = RoleNeed('user')
administrator_view = RoleNeed('administrator')
viewer_view = RoleNeed('viewer')

# Permissions
user = Permission(be_user)
administrator = Permission(be_admin)
viewers = Permission(be_viewer)
experts = Permission(be_expert)
administrator_view = Permission(administrator_view)
viewer_view = Permission(viewer_view)

apps_needs = [be_admin, be_viewer, be_user, be_expert, administrator_view, viewer_view]
apps_permissions = [user, administrator, viewers, experts, administrator_view, viewer_view]


@principal.identity_loader
def load_identity_when_session_expires():
    if hasattr(current_user, 'id'):
        return Identity(current_user.id)


@identity_loaded.connect
def on_identity_loaded(sender, identity):
    needs = []
    user = User.query.filter_by(email=identity.id).first()
    expert = Expert.query.filter_by(email=identity.id).first()
    viewer = Viewer.query.filter_by(email=identity.id).first()
    administrator = Admin.query.filter_by(email=identity.id).first()
    if user:
        needs.append(be_user)
    if expert or viewer or administrator:
        needs.append(be_expert)
    if viewer or administrator:
        needs.append(be_viewer)
    if administrator:
        needs.append(administrator_view)
        needs.append(be_admin)
    if viewer:
        needs.append(viewer_view)
    for n in needs:
        g.identity.provides.add(n)


@bp.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirects('base')

    mail = request.args.get('mail')

    # async_mail_proj(current_app.config['MAIL_USERNAME'])
    # mail_test()

    return render_template('base.html', auth=current_user.is_authenticated,
                           mail=mail)


@bp.route('/download')
def dwn():
    excel_letter()
    return redirect('base')


@bp.route('/excel/<project_number>', methods=['GET', 'POST'])
@viewers.require(http_exception=403)
def export_excel(project_number):
    data = User.query.all()
    data_list = [to_dict(item) for item in data]
    df1 = pd.DataFrame(data_list)

    df1['birthday'] = pd.to_datetime(df1['birthday']).dt.date
    excel_start_date = date(1899, 12, 30)
    try:
        df1['birthday'] = df1['birthday'] - excel_start_date
        df1.birthday = df1.birthday.dt.days
    except:
        pass

    parameters = Project.query.filter_by(number=project_number).first().parameters.all()
    i = 0
    for parameter in parameters:
        df1 = df1.rename(columns={"sum_grade_{}".format(i): parameter.name})
        i += 1
    while i < 10:
        df1 = df1.drop(columns={"sum_grade_{}".format(i)})
        i += 1

    df1['team'] = df1['team'].str.capitalize()
    df1['region'] = df1['region'].str.capitalize()

    for i in range(0, len(df1.index)):
        try:
            if 'λ' in str(df1.email[i]):
                a = len(df1.email[i]) - 1
                df1.email[i] = df1.email[i][:a]
        except:
            pass

    df1 = df1.rename(columns={"region": "Регион", "team": "Команда", "username": "ФИО", "birthday": "Дата рождения",
                              'photo': 'Ссылка на фотографию',
                              "sum_grade_all": "Итоговая оценка",
                              'project_id': 'ID'})  # надо будет добавить изменение имен через формы
    df1 = df1.fillna('-')
    df1 = df1.loc[df1['project_number'] == int(project_number)]
    df1 = df1.drop(columns=['password_hash', 'project_number'])
    names = df1.columns.values
    names_length = len(names)
    new_name = [names[0], names[1], names[3], names[2], names[4], names[5], names[6]]
    for i in range(8, names_length):
        new_name.append(names[i])
    new_name.append(names[7])
    df1 = df1.reindex(columns=new_name)
    data = Expert.query.all()
    data_list = [to_dict(item) for item in data]
    df2 = pd.DataFrame(data_list)

    df2 = df2.loc[df2['project_number'] == int(project_number)]
    df2 = df2.drop(columns=['password_hash', 'project_number'])
    df2.rename(columns={'username': 'ФИО', 'weight': 'Вес', 'project_id': 'ID',
                        'quantity': 'Количество выставленных оценок'}, inplace=True)
    data = Grade.query.all()
    data_list = [to_dict(item) for item in data]
    df3 = pd.DataFrame(data_list)
    df3.rename(columns={'date': 'Дата выставления оценки', 'comment': 'Комментарий'}, inplace=True)
    a = engine.execute("SELECT id FROM user WHERE project_number = ?", project_number)
    a = a.fetchall()
    f = []

    for i in range(len(df3.index)):
        c = 0
        for rows in a:
            b = engine.execute("SELECT project_id FROM user WHERE id = ?", rows[0])
            b = b.fetchall()
            if df3.user_id[i] == rows[0] and c == 0:
                df3.user_id[i] = b[0][0]
                c += 1
        if c == 0:
            f.append(int(i))
    a = engine.execute("SELECT id FROM expert WHERE project_number = ?", project_number)
    a = a.fetchall()

    for i in range(len(df3.index)):
        c = 0
        for row in a:
            b = engine.execute("SELECT project_id FROM expert WHERE id = ?", row[0])
            b = b.fetchall()
            if int(df3.expert_id[i]) == row[0] and c == 0:
                df3.expert_id[i] = b[0][0]
                c += 1

    for row in f:
        df3 = df3.drop([row])
    i = 0
    for parameter in parameters:
        df3 = df3.rename(columns={"parameter_{}".format(i): parameter.name})
        i += 1
    while i < 10:
        df3 = df3.drop(columns=["parameter_{}".format(i)])
        i += 1
    df3 = df3.drop(columns=['id'])
    df2 = df2.drop(columns=['id'])
    df1 = df1.drop(columns=['id'])
    df1.columns = [x.capitalize() for x in df1.columns]
    df1 = df1.rename(columns={'Id': 'ID', 'Фио': 'ФИО'})
    df3.rename(columns={'user_id': 'ID участника', 'expert_id': 'ID эксперта'}, inplace=True)

    filename = os.path.join(os.getcwd(), "{}.xlsx".format(Project.query.filter_by(number=project_number).first().name))

    writer = pd.ExcelWriter(filename, datetime_format='dd/mm/yyyy hh:mm', engine='xlsxwriter')
    df1.to_excel(writer, sheet_name='Участники', index=False, float_format="%.2f")
    workbook = writer.book
    base_format = workbook.add_format({'align': 'center'})
    new_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
    date_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'num_format': 'dd/mm/yyyy'})
    date2_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'num_format': 'dd/mm/yyyy hh:mm'})
    worksheet = writer.sheets['Участники']

    worksheet.set_column('A:Q', 21, base_format)
    worksheet.set_column('B:B', 35, base_format)
    worksheet.set_column('D:D', 24, base_format)
    worksheet.set_column('F:F', 26, base_format)
    worksheet.set_column('C:C', 14, date_format)

    df2.to_excel(writer, sheet_name='Эксперты', index=False)
    worksheet = writer.sheets['Эксперты']
    worksheet.set_column('A:E', 21, base_format)
    worksheet.set_column('B:B', 35, base_format)

    df3.to_excel(writer, sheet_name='Оценки', index=False)
    worksheet = writer.sheets['Оценки']
    worksheet.set_column('A:N', 30, new_format)
    worksheet.set_column('C:C', 24, date2_format)
    writer.save()

    return send_file(filename, as_attachment=True, cache_timeout=0)


# профиль пользователя
@bp.route('/user')
@user.require()
def user():
    user = User.query.filter_by(id=current_user.id).first()
    parameters = Parameter.query.filter_by(project_number=user.project_number).all()
    sum = []
    for i in range(10):
        x = getattr(user, 'sum_grade_{}'.format(i))
        if x:
            sum.append(round(x, 2))
        else:
            sum.append(0)
    return render_template('user_grades_table.html', title='Мои оценки',
                           user=user, project_number=user.project_number,
                           ParName=parameters, user_id=current_user.id, sum=sum, back='')


# ввод номера участника для перехода к выставлению оценки
@bp.route('/expert/<project_number>', methods=['GET', 'POST'])
@experts.require()
def expert(project_number):
    if current_user.id <= 1000000:
        return redirects()

    if 1200000 < current_user.id < 1300000:
        user = Admin.query.filter_by(id=current_user.id).first()
        expert = Expert.query.filter_by(email=user.email, project_number=project_number).first()
        back = url_for('main.admin_settings', project_number=project_number)
    elif 1100000 < current_user.id < 1200000:
        user = Viewer.query.filter_by(id=current_user.id).first()
        expert = Expert.query.filter_by(email=user.email, project_number=project_number).first()
        back = url_for('main.viewer_settings', project_number=project_number)
    else:
        expert = Expert.query.filter_by(id=current_user.id).first()
        back = None

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
    return render_template('expert.html', form=form, expert=expert, project_number=project_number, back=back)


# таблица оценок эксперта (для админа)
@bp.route('/expert_table_for_admin/<project_number>/<expert_id>', methods=['GET', 'POST'])
@administrator.require()
def expert_table_for_admin(project_number, expert_id):
    grades = Grade.query.filter_by(expert_id=expert_id).order_by(Grade.user_id).limit(20)
    expert = Expert.query.filter_by(id=expert_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()

    if request.method == 'POST':
        if request.files['photo']:
            os.chdir("app/static/images/{}/experts".format(project_number))
            photo = request.files['photo']
            photo.save(os.path.join(os.getcwd(), '{}.png').format(expert.project_id))
            compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(expert.project_id)))

    return render_template('expert_table_for_admin.html', title='Профиль эксперта',
                           grades=grades, expert=expert, project_number=project_number,
                           ParName=parameters,
                           back=url_for('main.admin_experts_table', project_number=project_number))


# таблица оценок эксперта (для наблюдателя)
@bp.route('/expert_table_for_viewer/<project_number>/<expert_id>', methods=['GET', 'POST'])
@viewers.require()
def expert_table_for_viewer(project_number, expert_id):
    grades = Grade.query.filter_by(expert_id=expert_id).order_by(Grade.user_id).limit(20)
    expert = Expert.query.filter_by(id=expert_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()

    if request.method == 'POST':
        if request.files['photo']:
            os.chdir("app/static/images/{}/experts".format(project_number))
            photo = request.files['photo']
            photo.save(os.path.join(os.getcwd(), '{}.png').format(expert.project_id))
            compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(expert.project_id)))

    return render_template('expert_table_for_viewer.html', title='Профиль эксперта',
                           grades=grades, expert=expert, project_number=project_number,
                           ParName=parameters,
                           back=url_for('main.viewer_experts_table', project_number=project_number))


# выставление оценки участнику
@bp.route('/expert/<project_number>/<user_id>', methods=['GET', 'POST'])
@experts.require()
def expert_grade(project_number, user_id):
    form = GradeForm()
    if form.validate_on_submit():
        if administrator_view.require():
            user = Admin.query.filter_by(id=current_user.id).first()
            expert = Expert.query.filter_by(email=user.email, project_number=project_number).first()
        elif 1100000 < current_user.id < 1200000:
            user = Viewer.query.filter_by(id=current_user.id).first()
            expert = Expert.query.filter_by(email=user.email, project_number=project_number).first()
        else:
            expert = Expert.query.filter_by(id=current_user.id).first()

        grade = Grade(user_id=user_id, expert_id=expert.id, comment=form.comment.data)
        grade_parameters = [form.parameter_0.data, form.parameter_1.data, form.parameter_2.data,
                            form.parameter_3.data, form.parameter_4.data, form.parameter_5.data,
                            form.parameter_6.data, form.parameter_7.data, form.parameter_8.data,
                            form.parameter_9.data]
        grade.set_points(grade_parameters)
        grade.date = datetime.now()
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

    return render_template('expert_grade.html', form=form, expert_id=current_user.id,
                           user=user, parameters=parameters, project_number=project_number)


# главня страница наблюдателя
@bp.route('/viewer', methods=['GET', 'POST'])
@viewers.require()
def viewer():
    viewer = Viewer.query.filter_by(id=current_user.id).first()
    projects = viewer.projects  # пары заказчик-проект из таблицы ViewerProjects
    proj = []  # сам проект и его даные

    for project in projects:
        proj.append(project.project)

    try:
        proj.sort(key=lambda Project: Project.start)
        proj.reverse()
    except:
        # proj не отсортировался
        pass

    return render_template('viewer_main.html', viewer=viewer, projects=proj, title='Проекты')


# страница Настройки проектов + доступ к юзерам и экспертам.
@bp.route('/viewer/settings/<project_number>', methods=['GET', 'POST'])
@viewers.require()
def viewer_settings(project_number):
    viewer = Viewer.query.filter_by(id=current_user.id).first()
    project = viewer.projects.filter_by(project_number=project_number) \
        .first().project

    if request.method == 'POST':
        # try:
        number = 0
        if request.files['users']:
            users = request.files['users']
            if len(User.query.filter_by(project_number=project_number).all()) > 0:
                number = User.query.filter_by(project_number=project_number).all()[-1].project_id
            else:
                number = 0
            users.filename = secure_filename_2(users.filename.rsplit(" ", 1)[0])
            os.chdir("app/static/images/{}".format(project_number))
            users.save(users.filename)
            os.chdir("../../../../")
            excel_user(users.filename, project.number)
            send_mail_new(project.number, 'users', number)

        if request.files['users_photo']:
            try:
                users_photo = request.files.getlist("users_photo")
                os.chdir("app/static/images/{}/users".format(project_number))
                for photo in users_photo:
                    photo.save(os.path.join(os.getcwd(), '{}.png').format(number + 1))
                    compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(number + 1)))
                    number += 1
                os.chdir('../../../../../')
            except:
                pass

        if request.files['experts']:
            experts = request.files['experts']
            if len(Expert.query.filter_by(project_number=project_number).all()) > 0:
                number = Expert.query.filter_by(project_number=project_number).all()[-1].project_id
            else:
                number = 0
            experts.filename = secure_filename_2(experts.filename.rsplit(" ", 1)[0])
            os.chdir("app/static/images/{}".format(project_number))
            experts.save(experts.filename)
            os.chdir("../../../../")
            excel_expert(experts.filename, project.number)
            send_mail_new(project.number, 'experts', number)

        if request.files['experts_photo']:
            try:
                experts_photo = request.files.getlist("experts_photo")
                os.chdir("app/static/images/{}/experts".format(project_number))
                for photo in experts_photo:
                    photo.save(os.path.join(os.getcwd(), '{}.png').format(number + 1))
                    compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(number + 1)))
                    number += 1
                os.chdir('../../../../../')
            except:
                pass

        project_settings(request, project, project_number)

    grade_access = \
        True if Expert.query.filter_by(email=viewer.email, project_number=project_number).first() is not None else False

    '''        return redirect(url_for('main.viewer_settings', project_number=project_number))
        else:
            flash('Что-то пошло не так', 'warning')
            return redirect(url_for('main.viewer_settings', project_number=project_number))'''

    return render_template('viewer_settings.html', viewer=viewer, project=project, title='Настройки проекта',
                           grade_acсess=grade_access, back=url_for('main.viewer'))


# таблица всех участников из проекта для наблюдателя
@bp.route('/viewer_users_table/<project_number>', methods=['GET', 'POST'])
@viewers.require()
def viewer_users_table(project_number):
    viewer = Viewer.query.filter_by(id=current_user.id).first()
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

    return render_template('viewer_users_table.html', title='Участники', viewer=viewer, teams=teams,
                           ParName=parameters, project_number=project_number, regions=regions,
                           project=project, back=url_for('main.viewer_settings', project_number=project_number))


# таблица личных оценок участника (для наблюдателя)
@bp.route('/user_grades_table_for_viewer/<project_number>/<user_id>', methods=['GET', 'POST'])
@viewers.require()
def user_grades_table_for_viewer(project_number, user_id):
    grades = Grade.query.filter_by(user_id=user_id).order_by(Grade.expert_id).limit(20)
    user = User.query.filter_by(id=user_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()

    if request.method == 'POST':
        if request.files['photo']:
            os.chdir("app/static/images/{}/users".format(project_number))
            photo = request.files['photo']
            photo.save(os.path.join(os.getcwd(), '{}.png').format(user.project_id))
            compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(user.project_id)))

    return render_template('user_grades_table_for_viewer.html', title='Оценки участника',
                           grades=grades, user=user, project_number=project_number,
                           ParName=parameters, user_id=user_id, len=len(parameters),
                           back=url_for('main.viewer_users_table', project_number=project_number))


# табллца экспертов для наблюдателя
@bp.route('/viewer_experts_table/<project_number>', methods=['GET', 'POST'])
@viewers.require()
def viewer_experts_table(project_number):
    viewer = Viewer.query.filter_by(id=current_user.id).first()
    project = Project.query.filter_by(number=project_number).first()
    parameters = project.parameters.all()

    return render_template('viewer_experts_table.html', title='Эксперты', viewer=viewer,
                           ParName=parameters, project_number=project_number, project=project,
                           back=url_for('main.viewer_settings', project_number=project_number))


# страница для создания нового проекта
@bp.route('/viewer/create_project', methods=['GET', 'POST'])
@viewers.require()
def create_project():
    try:
        with administrator_view.require():
            admin = Admin.query.filter_by(id=current_user.id).first()
            viewer = Viewer.query.filter_by(id=admin.viewer_id).first()
    except:
        viewer = Viewer.query.filter_by(id=current_user.id).first()

    if request.method == 'POST':
        result = request.form
        lvl = 0
        delete_project = False
        try:
            if result.get('name'):
                project = Project(name=result.get('name'))
                db.session.add(project)
                db.session.commit()
                proj = ViewerProjects(viewer_id=viewer.id, project_number=project.number)
                db.session.add(proj)
                db.session.commit()
                delete_project = True
                project = Project.query.all()[-1]
                for i in range(int(result.get('quantity'))):
                    if result.get('name{}'.format(i)).strip() != '':
                        db.session.add(Parameter(name=result.get('name{}'.format(i)).strip(),
                                                 weight=result.get('weight{}'.format(i)),
                                                 project_number=project.number))
                if result.get('start') and result.get('start') != 'дд.мм.гггг':
                    start = result.get('start')
                    setattr(project, 'start', datetime.strptime(start, '%d.%m.%y'))
                if result.get('end') and result.get('end') != 'дд.мм.гггг':
                    end = result.get('end')
                    setattr(project, 'end', datetime.strptime(end, '%d.%m.%y'))
                db.session.commit()
                os.chdir("app/static/images")
                lvl += 3
                if os.path.exists('{}'.format(project.number)):
                    shutil.rmtree('{}'.format(project.number))
                os.mkdir('{}'.format(project.number))
                os.chdir('{}'.format(project.number))
                os.mkdir('users'.format(project.number))
                os.mkdir('experts'.format(project.number))

                lvl += 1
                if request.files['logo']:
                    logo = request.files['logo']
                    logo.save(os.path.join(os.getcwd(), 'logo.png'.format(project.number)))
                os.chdir('../../../../')
                lvl = 0

                try:
                    if request.files['users']:
                        users = request.files['users']
                        users.filename = secure_filename_2(users.filename.rsplit(" ", 1)[0])
                        users.save(secure_filename_2(users.filename.rsplit(".", 1)[0]))
                        excel_user(users.filename, project.number)
                        send_mail_proj(project.number, 'user')
                except:
                    flash('Что-то не так с файлом участников', 'danger')
                    db.session.rollback()
                    return render_template('create_project.html', title='Создание проекта',
                                           form=result, back=url_for('main.viewer'))

                try:
                    if request.files['experts']:
                        experts = request.files['experts']
                        experts.filename = secure_filename_2(experts.filename.rsplit(" ", 1)[0])
                        experts.save(secure_filename_2(experts.filename.rsplit(".", 1)[0]))
                        excel_expert(experts.filename.rsplit(".", 1)[0], project.number)
                        # send_mail_proj(project.number, 'expert')
                except:
                    flash('Что-то не так с файлом экспертов', 'danger')
                    db.session.rollback()
                    return render_template('create_project.html', title='Создание проекта',
                                           form=result, back=url_for('main.viewer'))

                db.session.commit()

                flash('Проект создан', 'success')
                return redirect(url_for('main.viewer', viewer_id=current_user.id))
            else:
                flash('Заполните поле "Название проекта"', 'danger')
                db.session.rollback()
                return render_template('create_project.html', title='Создание проекта',
                                       form=result, back=url_for('main.viewer'))
        except:
            for i in range(lvl):
                os.chdir('../')
            flash('Что-то пошло не так. Проверьте корректность данных.', 'danger')
            db.session.rollback()
            if delete_project:

                project = Project.query.all()[-1]
                proj = ViewerProjects.query.filter_by(project_number=project.number).first()
                if proj:
                    db.session.delete(proj)
                for parameter in project.parameters.all():
                    db.session.delete(parameter)

                os.chdir("app/static/images")
                try:
                    if os.path.exists('{}'.format(project.number)):
                        shutil.rmtree('{}'.format(project.number))
                except:
                    pass
                os.chdir('../../../')

                db.session.delete(project)
                db.session.commit()
            return render_template('create_project.html', title='Создание проекта',
                                   form=request.form, back=url_for('main.viewer'))

    return render_template('create_project.html', title='Создание проекта', back=url_for('main.viewer'))


# добавление участника
@bp.route('/add_new_user/<project_number>', methods=['GET', 'POST'])
@viewers.require()
def add_new_user(project_number):
    if request.method == 'POST':
        result = request.form

        if result.get('username') and result.get('email') and \
                result.get('birthday') != 'дд.мм.гггг':
            if User.query.filter_by(email=result.get('email')).first() is None:
                users = User.query.filter_by(project_number=project_number).all()
                if users:
                    last_user_id = users[-1].project_id
                else:
                    last_user_id = 0

                user = User(project_number=project_number, username=result.get('username'),
                            email=result.get('email'), project_id=last_user_id + 1)

                db.session.add(user)
                db.session.commit()

                user = User.query.filter_by(project_number=project_number, project_id=last_user_id + 1).first()

                if result.get('birthday'):
                    setattr(user, 'birthday', datetime.strptime(result.get('birthday'), '%d.%m.%Y'))

                if result.get('team'):
                    setattr(user, 'team', result.get('team'))

                if result.get('region'):
                    setattr(user, 'region', result.get('region'))

                if result.get('photo'):
                    setattr(user, 'photo', result.get('photo'))

                password = password_generator()
                user.set_password(password)
                try:
                    send_password_mail(user, password)
                except:
                    db.session.delete(user)
                    db.session.commit()
                    flash('Возможно пользователь с данной почтой уже зарегистрирован', 'warning')
                    if (current_user.id <= 1200000):
                        return redirect(url_for('main.viewer_settings', project_number=project_number))
                    else:
                        return redirect(url_for('main.admin_settings', project_number=project_number))

                db.session.commit()

                flash('Участник добавлен', 'success')
                if (current_user.id <= 1200000):
                    return redirect(url_for('main.viewer_settings', project_number=project_number))
                else:
                    return redirect(url_for('main.admin_settings', project_number=project_number))
            else:
                flash('Возможно пользователь с данной почтой уже зарегистрирован', 'warning')
        else:
            flash('Проверьте корректность введённых данных', 'warning')

    if (current_user.id <= 1200000):
        return render_template('add_new_user.html', title='Добавление участника',
                               project_number=project_number,
                               back=url_for('main.viewer_settings', project_number=project_number))
    else:
        return render_template('add_new_user.html', title='Добавление участника',
                               project_number=project_number,
                               back=url_for('main.admin_settings', project_number=project_number))


# добавление эксперта
@bp.route('/add_new_expert/<project_number>', methods=['GET', 'POST'])
@viewers.require()
def add_new_expert(project_number):
    if request.method == 'POST':
        result = request.form
        if result.get('username') and result.get('email'):
            if Expert.query.filter_by(email=result.get('email')).first() is None:
                experts = Expert.query.filter_by(project_number=project_number).all()
                if experts:
                    last_expert_id = experts[-1].project_id
                else:
                    last_expert_id = 0

                expert = Expert(project_number=project_number, username=result.get('username'),
                                email=result.get('email'), project_id=last_expert_id + 1)

                db.session.add(expert)
                db.session.commit()

                expert = Expert.query.filter_by(project_number=project_number, project_id=last_expert_id + 1).first()

                if result.get('weight'):
                    setattr(expert, 'weight', result.get('weight'))

                if result.get('photo'):
                    setattr(expert, 'photo', result.get('photo'))

                password = password_generator()
                expert.set_password(password)
                try:
                    send_password_mail(expert, password)
                except:
                    db.session.delete(expert)
                    db.session.commit()
                    flash('Возможно пользователь с данной почтой уже зарегистрирован', 'warning')
                    if (current_user.id <= 1200000):
                        return redirect(url_for('main.viewer_settings', project_number=project_number))
                    else:
                        return redirect(url_for('main.admin_settings', project_number=project_number))

                db.session.commit()
                flash('Эксперт добавлен', 'success')
                if (current_user.id <= 1200000):
                    return redirect(url_for('main.viewer_settings', project_number=project_number))
                else:
                    return redirect(url_for('main.admin_settings', project_number=project_number))
            else:
                flash('Возможно пользователь с данной почтой уже зарегистрирован', 'warning')
        else:
            flash('Проверьте корректность введённых данных', 'warning')

    if (current_user.id <= 1200000):
        return render_template('add_new_expert.html', title='Добавление участника',
                               project_number=project_number,
                               back=url_for('main.viewer_settings', project_number=project_number))
    else:
        return render_template('add_new_expert.html', title='Добавление участника',
                               project_number=project_number,
                               back=url_for('main.admin_settings', project_number=project_number))


# главная страница админа
@bp.route('/admin', methods=['GET', 'POST'])
@administrator.require()
def admin():
    admin = Admin.query.filter_by(id=current_user.id).first()

    return render_template('admin_main.html', admin=admin)


# страница со всеми проектами
@bp.route('/admin/projects', methods=['GET', 'POST'])
@administrator.require()
def admin_projects():
    admin = Admin.query.filter_by(id=current_user.id).first()
    projects = Project.query.order_by(Project.start.desc()).all()

    return render_template('admin_projects.html', admin=admin, projects=projects, title='Проекты',
                           back=url_for('main.admin'))


# страница Настройки проектов + доступ к юзерам и экспертам.
@bp.route('/admin/settings/<project_number>', methods=['GET', 'POST'])
@administrator.require()
def admin_settings(project_number):
    admin = Admin.query.filter_by(id=current_user.id).first()
    project = Project.query.filter_by(number=project_number).first()

    if request.method == 'POST':
        # try:

        if request.files['users']:
            users = request.files['users']
            number = User.query.filter_by(project_number=project_number).all()[-1].project_id
            users.filename = secure_filename_2(users.filename.rsplit(" ", 1)[0])
            users.save(secure_filename_2(users.filename.rsplit(".", 1)[0]))
            excel_user(users.filename, project.number)
            send_mail_new(project.number, 'users', number)

        if request.files['experts']:
            experts = request.files['experts']
            number = Expert.query.filter_by(project_number=project_number).all()[-1].project_id
            experts.filename = secure_filename_2(experts.filename.rsplit(" ", 1)[0])
            experts.save(secure_filename_2(experts.filename.rsplit(".", 1)[0]))
            excel_expert(experts.filename, project.number)
            send_mail_new(project.number, 'experts', number)

        project_settings(request, project, project_number)

    grade_access = \
        True if Expert.query.filter_by(email=admin.email, project_number=project_number).first() is not None else False

    '''        return redirect(url_for('main.admin_settings', project_number=project_number))
        else:
            flash('Что-то пошло не так', 'warning')
            return redirect(url_for('main.admin_settings', project_number=project_number))'''

    return render_template('admin_settings.html', admin=admin, project=project, grade_access=grade_access,
                           back=url_for('main.admin_projects'))


# таблица всех участников из проекта для админа
@bp.route('/admin_users_table/<project_number>', methods=['GET', 'POST'])
@administrator.require()
def admin_users_table(project_number):
    admin = Admin.query.filter_by(id=current_user.id).first()
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
                           project=project, back=url_for('main.admin_settings', project_number=project_number))


# таблица экспертов
@bp.route('/admin_experts_table/<project_number>', methods=['GET', 'POST'])
@administrator.require()
def admin_experts_table(project_number):
    admin = Admin.query.filter_by(id=current_user.id).first()
    project = Project.query.filter_by(number=project_number).first()
    parameters = project.parameters.all()

    return render_template('admin_experts_table.html', title='Эксперты', admin=admin,
                           ParName=parameters, project_number=project_number, project=project,
                           back=url_for('main.admin_settings', project_number=project_number))


# страница для выдачи ролей
@bp.route('/admin_waiting_users', methods=['GET', 'POST'])
@administrator.require()
def admin_waiting_users():
    waiting_users = WaitingUser.query.limit(15)

    return render_template('admin_waiting_users.html', waiting_users=waiting_users,
                           back=url_for('main.admin'))


@bp.route('/admin_viewers', methods=['GET', 'POST'])
@administrator.require()
def admin_viewers():
    viewers = Viewer.query.limit(10)

    return render_template('admin_viewers.html', viewers=viewers, back=url_for('main.admin'))


@bp.route('/unappended_viewers/<project_number>', methods=['GET', 'POST'])
@administrator.require()
def unappended_viewers(project_number):
    return render_template("unappended_viewers.html", project_number=project_number,
                           back=url_for('main.admin_settings', project_number=project_number))


# таблица личных оценок участника (для админа)
@bp.route('/user_grades_table_for_admin/<project_number>/<user_id>', methods=['GET', 'POST'])
@administrator.require()
def user_grades_table_for_admin(project_number, user_id):
    grades = Grade.query.filter_by(user_id=user_id).order_by(Grade.expert_id).limit(20)
    user = User.query.filter_by(id=user_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()

    if request.method == 'POST':
        if request.files['photo']:
            os.chdir("app/static/images/{}/users".format(project_number))
            photo = request.files['photo']
            photo.save(os.path.join(os.getcwd(), '{}.png').format(user.project_id))
            compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(user.project_id)))

    return render_template('user_grades_table_for_admin.html', title='Оценки участника',
                           grades=grades, user=user, project_number=project_number,
                           ParName=parameters, user_id=user_id, len=len(parameters),
                           back=url_for('main.admin_users_table', project_number=project_number))


# сортировка таблицы участников или увелечение количества участников в таблице
@bp.route('/sort_users_table', methods=['POST'])
@bp.route('/show_more_users', methods=['POST'])
@login_required
def users_table():
    if int(request.form['lim']) < 15:
        limit = 15
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
                users = users.order_by(User.__dict__[request.form['parameter']].asc()).all()
            else:
                users = users.order_by(User.__dict__[request.form['parameter']].desc()).all()
        else:
            if request.form['parameter'] == 'birthday':
                users = users.order_by(User.__dict__[request.form['parameter']].desc()).all()
            else:
                users = users.order_by(User.__dict__[request.form['parameter']].asc()).all()
    else:
        users = users.order_by(User.project_id).all()

    # сортировка по возрасту
    t = date.today()
    new_users = []
    for user in users:
        if user.birthday is not None:
            age = t.year - int(user.birthday.strftime('%Y')) - \
                  ((t.month, t.day) <
                   (int(user.birthday.strftime('%m')),
                    int(user.birthday.strftime('%d'))))
            if int(request.form['min_age']) <= age <= int(request.form['max_age']):
                new_users.append(user)
        else:
            new_users.append(user)

    return jsonify({'users': users_in_json(new_users[:limit])})


@bp.route('/sort_experts_table', methods=['POST'])
@bp.route('/show_more_experts', methods=['POST'])
@login_required
def show_more_experts():
    if int(request.form['lim']) < 15:
        limit = 15
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
    if int(request.form['lim']) < 15:
        limit = 15
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

    lenght = len(Project.query.filter_by(number=User.query.filter_by(id=request.form['user_id'])
                                         .first().project_number).first().parameters.all())

    return jsonify({'grades': grades_in_json(grades, lenght)})


# добавление оценок эксперта в таблицу или сортировка оценок эксперта
@bp.route('/show_more_grades_for_expert', methods=['POST'])
@bp.route('/sort_grades_table_for_expert', methods=['POST'])
@login_required
def show_more_grades_for_expert():
    if int(request.form['lim']) < 15:
        limit = 15
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

    lenght = len(Project.query.filter_by(number=Expert.query.filter_by(id=request.form['expert_id'])
                                         .first().project_number).first().parameters.all())

    return jsonify({'grades': grades_in_json(grades, lenght)})


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
        expert = Expert(username=waiting_user.username, email=waiting_user.email,
                        password_hash=waiting_user.password_hash)
        db.session.add(expert)
        db.session.commit()

        expert = Expert.query.filter_by(username=waiting_user.username, email=waiting_user.email).first()
        setattr(expert, 'project_id', expert.id)
        if request.form['role'] == 'Администратор':
            user = Admin(username=waiting_user.username, email=waiting_user.email,
                         password_hash=waiting_user.password_hash,
                         phone_number=waiting_user.phone_number, expert_id=expert.id)
            viewer = Viewer(username=waiting_user.username, email=waiting_user.email,
                            password_hash=waiting_user.password_hash, organization=waiting_user.organization,
                            phone_number=waiting_user.phone_number, expert_id=expert.id)
            send_role_update(user, 'Администратор')
            db.session.add(viewer)

        elif request.form['role'] == 'Заказчик':
            user = Viewer(username=waiting_user.username, email=waiting_user.email,
                          password_hash=waiting_user.password_hash,
                          phone_number=waiting_user.phone_number, expert_id=expert.id,
                          organization=waiting_user.organization)
            send_role_update(user, 'Заказчик')

        elif request.form['role'] == 'Удалить':
            db.session.delete(waiting_user)
            db.session.commit()
            send_role_refuse(waiting_user)
            return jsonify({'result': 'deleted'})
        else:
            return jsonify({'result': 'error'})

        db.session.add(user)
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
        try:
            os.chdir('app/static/images/{}/users'.format(user.project_number))
            try:
                old_img = os.path.join(os.getcwd(), '{}.png'.format(user.project_id))
                if os.path.exists(old_img):
                    os.remove(old_img)
            except:
                pass
            os.chdir('../../../../../')
        except:
            pass

        for grade in user.grades.all():
            t_expert = grade.expert

            db.session.delete(grade)
            setattr(t_expert, 'quantity', getattr(t_expert, 'quantity') - 1)

    elif role == 'expert':
        user = Expert.query.filter_by(id=request.form['id']).first()

        os.chdir('app/static/images/{}/experts'.format(user.project_number))
        try:
            old_img = os.path.join(os.getcwd(), '{}.png'.format(user.project_id))
            if os.path.exists(old_img):
                os.remove(old_img)
        except:
            pass
        os.chdir('../../../../../')
        for grade in user.grades.all():
            t_user = grade.user
            db.session.delete(grade)
            t_user.sum_grades()
    elif role == 'waiting_user':
        user = WaitingUser.query.filter_by(id=request.form['id']).first()
    elif role == 'viewer':
        user = Viewer.query.filter_by(id=request.form['id']).first()
        expert = Expert.query.filter_by(id=user.expert_id).first()
        if expert:
            db.session.delete(expert)
    elif role == 'admin':
        user = Admin.query.filter_by(id=request.form['id']).first()
        expert = Expert.query.filter_by(id=user.expert_id).first()
        viewer = Viewer.query.filter_by(id=user.viewer_id).first()
        if expert:
            db.session.delete(expert)
        if viewer:
            db.session.delete(viewer)
    else:
        return jsonify({'result': 'User not found'})

    db.session.delete(user)
    db.session.commit()
    return jsonify({'result': 'success'})


@bp.route('/delete_project', methods=['POST'])
@login_required
def delete_project():
    project = Project.query.filter_by(number=request.form['number']).first()

    for parameter in project.parameters.all():
        db.session.delete(parameter)

    for viewer in project.viewers.all():
        db.session.delete(viewer)

    for user in User.query.filter_by(project_number=project.number).all():
        for grade in user.grades.all():
            db.session.delete(grade)
        db.session.delete(user)
    for expert in Expert.query.filter_by(project_number=project.number).all():
        db.session.delete(expert)
    db.session.delete(project)
    db.session.commit()
    os.chdir("app/static/images")
    try:
        if os.path.exists('{}'.format(project.number)):
            shutil.rmtree('{}'.format(project.number))
    except:
        pass
    os.chdir('../../../')

    return jsonify({'result': 'success'})


# увелечение количества отображаемых пользователей в таблице раздачи ролей
# сортировка таблицы зарегистрированных пользователей
@bp.route('/show_more_waiting_users', methods=['POST'])
@bp.route('/sort_waiting_users', methods=['POST'])
@login_required
def show_more_waiting_users():
    if request.form['parameter'] != '':
        if request.form['sort_up'] == 'true':

            waiting_users = WaitingUser.query \
                .order_by(WaitingUser.__dict__[request.form['parameter']].desc()) \
                .limit(int(request.form['lim']) + 1)

        else:
            waiting_users = WaitingUser.query \
                .order_by(WaitingUser.__dict__[request.form['parameter']].asc()) \
                .limit(int(request.form['lim']) + 1)
    else:
        waiting_users = WaitingUser.query \
            .order_by(WaitingUser.project_id).limit(int(request.form['lim']) + 1)

    return jsonify({'waiting_users': waiting_users_in_json(waiting_users)})


@bp.route('/save_expert_data', methods=['POST'])
@login_required
def save_expert_data():
    data = list(json.loads(request.form['data']))
    expert = Expert.query.filter_by(id=request.form['expert_id']).first()

    if getattr(expert, 'username') != data[0]:
        d0 = data[0].strip().capitalize()
        if d0 != '':
            setattr(expert, 'username', d0)

    if getattr(expert, 'weight') != data[1]:
        setattr(expert, 'weight', data[1])

    if getattr(expert, 'email') != data[2]:
        d2 = data[2].strip().lower()
        if d2 != '':
            setattr(expert, 'email', d2)

    if getattr(expert, 'password_hash') != data[3]:
        d3 = data[3].strip()
        if d3 != '':
            setattr(expert, 'password_hash', d3)

    if getattr(expert, 'photo') != data[4]:
        d4 = data[4].strip()
        if d4 != '':
            setattr(expert, 'photo', d4)

    db.session.commit()

    return jsonify({'result': 'successfully'})


@bp.route('/save_user_data', methods=['POST'])
@login_required
def save_user_data():
    data = list(json.loads(request.form['data']))
    user = User.query.filter_by(id=request.form['user_id']).first()

    if getattr(user, 'username') != data[0]:
        d1 = data[0].strip().capitalize()
        if d1 != '':
            setattr(user, 'username', data[0])

    if getattr(user, 'team') != data[2].capitalize():
        d2 = data[2].strip().capitalize()
        if d2 != '':
            setattr(user, 'team', d2)

    if getattr(user, 'region') != data[3]:
        d3 = data[3].strip().capitalize()
        if d3 != '':
            setattr(user, 'region', d3)

    if len(data) >= 5:
        if getattr(user, 'email') != data[4]:
            d4 = data[4].strip().lower()
            if d4 != '':
                setattr(user, 'email', d4)

    if getattr(user, 'password_hash', ) != data[5]:
        d5 = data[5].strip()
        if d5 != '':
            setattr(user, 'password_hash', d5)

    '''
    if getattr(user, 'photo') != data[6]:
        d6 = data[6].strip()
        if d6 != '':
            setattr(user, 'photo', d6)'''

    db.session.commit()

    try:
        if data[1] and getattr(user, 'password_hash', ) != datetime.strptime(data[1], '%Y-%m-%d'):
            setattr(user, 'birthday', datetime.strptime(data[1], '%Y-%m-%d'))
        else:
            setattr(user, 'birthday', sql_null)
        db.session.commit()
    except:
        return jsonify({'result': 'error'})

    return jsonify({'result': 'successfully'})


@bp.route('/show_more_viewers', methods=['POST'])
@bp.route('/sort_viewers', methods=['POST'])
@login_required
def show_more_viewers():
    if request.form['parameter'] != '':
        if request.form['sort_up'] == 'true':

            viewers = Viewer.query \
                .order_by(Viewer.__dict__[request.form['parameter']].desc()) \
                .limit(int(request.form['lim']) + 1)

        else:
            viewers = Viewer.query \
                .order_by(Viewer.__dict__[request.form['parameter']].asc()) \
                .limit(int(request.form['lim']) + 1)
    else:
        viewers = Viewer.query \
            .order_by(Viewer.id).limit(int(request.form['lim']) + 1)

    return jsonify({'viewers': viewers_in_json(viewers)})


@bp.route('/unappend_viewer', methods=['GET', 'POST'])
def unappend_viewer():
    viewer = ViewerProjects.query.filter_by(project_number=request.form['project_number'],
                                            viewer_id=request.form['viewer_id']).first()
    if viewer:
        db.session.delete(viewer)
        db.session.commit()
    else:
        return jsonify({'result': 'not_found_error'})

    return jsonify({'result': 'success'})


# прикрепляет заказчика к проекту
@bp.route('/append_viewer', methods=['GET', 'POST'])
def append_viewer():
    try:
        new_viewer = ViewerProjects(project_number=request.form['project_number'],
                                    viewer_id=request.form['viewer_id'])

        db.session.add(new_viewer)
        db.session.commit()

        return jsonify({'result': 'success'})
    except:
        return jsonify({'result': 'error'})


@bp.route('/sort_unappend_viewers', methods=['GET', 'POST'])
def sort_unappend_viewers():
    if request.form['parameter'] != '':
        if request.form['sort_up'] == 'true':
            viewers = Viewer.query \
                .order_by(Viewer.__dict__[request.form['parameter']].desc()) \
                .all()
        else:
            viewers = Viewer.query \
                .order_by(Viewer.__dict__[request.form['parameter']].asc()) \
                .all()
    else:
        viewers = Viewer.query.order_by(Viewer.id).all()
    viewers2 = []
    for viewer in viewers:
        x = True
        for project in viewer.projects.all():
            if project.project_number == int(request.form['project_number']):
                x = False
        if x:
            viewers2.append(viewer)

    return jsonify({'viewers': viewers_in_json(viewers2)})
