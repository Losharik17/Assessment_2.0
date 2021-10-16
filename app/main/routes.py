import datetime
import json
import password as password
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app, send_file
from flask_login import current_user, login_required
from app import db
from app.main.forms import EmptyForm, GradeForm, UserForm, UserRegistrationForm, ExpertRegistrationForm
from app.models import User, Expert, Grade, Viewer, Admin, Parameter, Project, WaitingUser
from app.main import bp
from app.main.functions import users_in_json, experts_in_json, grades_in_json, \
    waiting_users_in_json, viewers_in_json, \
    excel_expert, excel_user, to_dict, delete_timer, redirects, compression, password_generator, \
    send_password_mail, password_generator
from app.auth.email import send_role_update, send_role_refuse
import pandas as pd
from app.main.secure_filename_2 import secure_filename_2
import os
from datetime import date, datetime
import shutil
from sqlalchemy import create_engine

from werkzeug.security import generate_password_hash
from threading import Thread
from flask_mail import Message
from app import mail
import math


engine = create_engine("sqlite:///T_Park.db")


@bp.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return redirects('base')
    return render_template('base.html', auth=current_user.is_authenticated)


@bp.route('/download')
@login_required
def dwn():
    if current_user.id <= 1100000:
        return redirects()
    return render_template('download.html')


@bp.route('/excel/<project_number>', methods=['GET', 'POST'])
@login_required
def export_excel(project_number):
    if current_user.id <= 1100000:
        return redirects()

    data = User.query.all()
    data_list = [to_dict(item) for item in data]
    df1 = pd.DataFrame(data_list)

    df1['birthday'] = pd.to_datetime(df1['birthday']).dt.date
    excel_start_date = date(1899, 12, 30)
    df1['birthday'] = df1['birthday'] - excel_start_date
    df1.birthday = df1.birthday.dt.days

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
    df2 = df2.drop(columns=['password_hash', 'project_number', 'quantity'])
    df2.rename(columns={'username': 'ФИО', 'weight': 'Вес', 'project_id': 'ID'}, inplace=True)
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
    df1.to_excel(writer, sheet_name='Участники', index=False, float_format="%.1f")
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
    worksheet.set_column('A:D', 21, base_format)
    worksheet.set_column('B:B', 35, base_format)

    df3.to_excel(writer, sheet_name='Оценки', index=False)
    worksheet = writer.sheets['Оценки']
    worksheet.set_column('A:N', 30, new_format)
    worksheet.set_column('C:C', 24, date2_format)
    writer.save()
    os.chdir('../../../../../')

    return send_file(filename, as_attachment=True, cache_timeout=0)


# профиль пользователя
@bp.route('/user')
@login_required
def user():
    if 1000000 < current_user.id:
        return redirects()

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
@login_required
def expert(project_number):
    if current_user.id <= 1000000:
        return redirects()

    if 1200000 < current_user.id < 1300000:
        user = Admin.query.filter_by(id=current_user.id).first()
        expert = Expert.query.filter_by(id=user.expert_id).first()
        back = url_for('main.admin_settings', project_number=project_number)
    elif 1100000 < current_user.id < 1200000:
        user = Viewer.query.filter_by(id=current_user.id).first()
        expert = Expert.query.filter_by(id=user.expert_id).first()
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
@login_required
def expert_table_for_admin(project_number, expert_id):
    if current_user.id <= 1200000:
        return redirects()
    grades = Grade.query.filter_by(expert_id=expert_id).order_by(Grade.user_id).limit(20)
    expert = Expert.query.filter_by(id=expert_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()

    if request.method == 'POST' and request.files['photo']:
        os.chdir('app/static/images/{}/experts'.format(project_number))
        try:
            old_img = os.path.join(os.getcwd(), '{}.png'.format(expert.project_id))
            if os.path.exists(old_img):
                os.remove(old_img)
            img = request.files['photo']
            img.save(os.path.join(os.getcwd(), '{}.png'.format(expert.project_id)))
            compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(expert.project_id)))
        except:
            flash('Не удалось сохранить фото', 'warning')
            return redirect(url_for('main.expert_table_for_admin',
                                    project_number=project_number, expert_id=expert_id))
        os.chdir('../../../../../')
        flash('Изменения сохранены', 'success')
        return redirect(url_for('main.expert_table_for_admin',
                                project_number=project_number, expert_id=expert_id))

    return render_template('expert_table_for_admin.html', title='Профиль эксперта',
                           grades=grades, expert=expert, project_number=project_number,
                           ParName=parameters,
                           back=url_for('main.admin_experts_table', project_number=project_number))


# таблица оценок эксперта (для наблюдателя)
@bp.route('/expert_table_for_viewer/<project_number>/<expert_id>', methods=['GET', 'POST'])
@login_required
def expert_table_for_viewer(project_number, expert_id):
    if current_user.id <= 1100000:
        return redirects()
    grades = Grade.query.filter_by(expert_id=expert_id).order_by(Grade.user_id).limit(20)
    expert = Expert.query.filter_by(id=expert_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()

    if request.method == 'POST' and request.files['photo']:
        os.chdir('app/static/images/{}/experts'.format(project_number))
        try:
            old_img = os.path.join(os.getcwd(), '{}.png'.format(expert.project_id))
            if os.path.exists(old_img):
                os.remove(old_img)
            img = request.files['photo']
            img.save(os.path.join(os.getcwd(), '{}.png'.format(expert.project_id)))
            compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(expert.project_id)))
        except:
            flash('Не удалось сохранить фото', 'warning')
            return redirect(url_for('main.expert_table_for_viewer',
                                    project_number=project_number, expert_id=expert_id))
        os.chdir('../../../../../')
        flash('Изменения сохранены', 'success')
        return redirect(url_for('main.expert_table_for_viewer',
                                project_number=project_number, expert_id=expert_id))

    return render_template('expert_table_for_viewer.html', title='Профиль эксперта',
                           grades=grades, expert=expert, project_number=project_number,
                           ParName=parameters,
                           back=url_for('main.viewer_experts_table', project_number=project_number))


# выставление оценки участнику
@bp.route('/expert/<project_number>/<user_id>', methods=['GET', 'POST'])
@login_required
def expert_grade(project_number, user_id):
    if current_user.id <= 1000000:
        return redirects()
    form = GradeForm()
    if form.validate_on_submit():
        if 1200000 < current_user.id < 1300000:
            user = Admin.query.filter_by(id=current_user.id).first()
            expert = Expert.query.filter_by(id=user.expert_id).first()
        elif 1100000 < current_user.id < 1200000:
            user = Viewer.query.filter_by(id=current_user.id).first()
            expert = Expert.query.filter_by(id=user.expert_id).first()
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
@login_required
def viewer():
    if current_user.id <= 1100000 or current_user.id > 1200000:
        return redirects()
    viewer = Viewer.query.filter_by(id=current_user.id).first()
    proj = []
    for viewer in Viewer.query.filter_by(organization=viewer.organization).all():
        proj += viewer.projects.all()

    try:
        proj.sort(key=lambda Project: Project.start)
        proj.reverse()
    except:
        pass

    return render_template('viewer_main.html', viewer=viewer, projects=proj, title='Проекты')


# страница Настройки проектов + доступ к юзерам и экспертам.
@bp.route('/viewer/settings/<project_number>', methods=['GET', 'POST'])
@login_required
def viewer_settings(project_number):
    if current_user.id <= 1100000 or current_user.id > 1200000:
        return redirects()
    viewer = Viewer.query.filter_by(id=current_user.id).first()
    project = viewer.projects.filter_by(number=project_number).first()

    if request.method == 'POST':
        # try:
        result = request.form

        if request.files['users'] and request.files['users_photo']:
            users = request.files['users']
            number = User.query.filter_by(project_number=project_number).all()[-1].project_id
            users.filename = secure_filename_2(users.filename.rsplit(" ", 1)[0])
            users.save(secure_filename_2(users.filename.rsplit(".", 1)[0]))
            excel_user(users.filename, project.number)

            users_photo = request.files.getlist("users_photo")

            def async_mail_ex(ap, project_number, number):
                engine = create_engine("sqlite:////var/www/fastuser/data/www/rating.nspt.ru/T_Park.db")
                with ap.app_context():
                    users = User.query.filter_by(project_number=project_number).all()
                    for i in range(number):
                        users.pop(0)

                    for user in users:
                        passw = password_generator()
                        engine.execute("UPDATE user SET password_hash = ? WHERE email = ?",
                                       generate_password_hash(passw), user.email)
                        msg = Message('NSPT Ваш пароль', sender=current_app.config['MAIL_USERNAME'],
                                      recipients=[user.email])
                        msg.body = render_template('email/send_password.txt',
                                                   user=user, password=passw)
                        msg.html = render_template('email/send_password.html',
                                                   user=user, password=passw)
                        mail.send(msg)


            def ex_mail(project_number, number):
                from main import app as ap
                Thread(target=async_mail_ex,
                       args=(ap, project_number, number)).start()

            ex_mail(project.number, number)

            os.chdir("app/static/images/{}/users".format(project_number))
            for photo in users_photo:
                photo.save(os.path.join(os.getcwd(), '{}.png').format(number + 1))
                compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(number + 1)))
                number += 1
            os.chdir('../../../../../')


        if request.files['experts'] and request.files['experts_photo']:
            experts = request.files['experts']
            number = Expert.query.filter_by(project_number=project_number).all()[-1].project_id
            experts.filename = secure_filename_2(experts.filename.rsplit(" ", 1)[0])
            experts.save(secure_filename_2(experts.filename.rsplit(".", 1)[0]))
            excel_expert(experts.filename, project.number)

            experts_photo = request.files.getlist("experts_photo")
            
            def async_mail_ex_2(ap, project_number, number):
                engine = create_engine("sqlite:////var/www/fastuser/data/www/rating.nspt.ru/T_Park.db")
                with ap.app_context():
                    users = Expert.query.filter_by(project_number=project_number).all()
                    for i in range(number):
                        users.pop(0)

                    for user in users:
                        passw = password_generator()
                        engine.execute("UPDATE expert SET password_hash = ? WHERE email = ?",
                                       generate_password_hash(passw), user.email)
                        msg = Message('NSPT Ваш пароль', sender=current_app.config['MAIL_USERNAME'],
                                      recipients=[user.email])
                        msg.body = render_template('email/send_password.txt',
                                                   user=user, password=passw)
                        msg.html = render_template('email/send_password.html',
                                                   user=user, password=passw)
                        mail.send(msg)


            def ex_mail_2(project_number, number):
                from main import app as ap
                Thread(target=async_mail_ex_2,
                       args=(ap, project_number, number)).start()

            ex_mail_2(project.number, number)

            os.chdir("app/static/images/{}/users".format(project_number))
            for photo in experts_photo:
                photo.save(os.path.join(os.getcwd(), '{}.png').format(number + 1))
                compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(number + 1)))
                number += 1
            os.chdir('../../../../../')


        if request.files['logo']:
            os.chdir('app/static/images/{}'.format(project_number))
            logo = request.files['logo']
            logo.save(os.path.join(os.getcwd(), '{}.png'.format(project.number)))
            os.chdir('../../../../')

        if result.get('name') and result.get('start') and result.get('end'):
            setattr(project, 'name', result.get('name'))
            setattr(project, 'start', datetime.strptime(result.get('start'), '%d.%m.%y'))
            setattr(project, 'end', datetime.strptime(result.get('end'), '%d.%m.%y'))
            db.session.commit()
            flash('Изменения сохранены', 'success')
            return redirect(url_for('main.viewer_settings', project_number=project_number))
        else:
            flash('Что-то пошло не так', 'warning')
            return redirect(url_for('main.viewer_settings', project_number=project_number))

    return render_template('viewer_settings.html', viewer=viewer, project=project, title='Настройки проекта',
                           back=url_for('main.viewer'))


# таблица всех участников из проекта для наблюдателя
@bp.route('/viewer_users_table/<project_number>', methods=['GET', 'POST'])
@login_required
def viewer_users_table(project_number):
    if current_user.id <= 1100000 or current_user.id > 1200000:
        return redirects()
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
@login_required
def user_grades_table_for_viewer(project_number, user_id):
    if current_user.id <= 1100000:
        return redirects()
    grades = Grade.query.filter_by(user_id=user_id).order_by(Grade.expert_id).limit(20)
    user = User.query.filter_by(id=user_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()

    if request.method == 'POST' and request.files['photo']:
        os.chdir('app/static/images/{}/users'.format(project_number))
        try:
            old_img = os.path.join(os.getcwd(), '{}.png'.format(user.project_id))
            if os.path.exists(old_img):
                os.remove(old_img)
            img = request.files['photo']
            img.save(os.path.join(os.getcwd(), '{}.png'.format(user.project_id)))
            compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(user.project_id)))
        except:
            flash('Не удалось сохранить фото', 'warning')
            return redirect(url_for('main.user_grades_for_viewer',
                                    project_number=project_number, expert_id=user_id))

        os.chdir('../../../../../')
        flash('Изменения сохранены', 'success')
        return redirect(url_for('main.user_grades_table_for_viewer',
                                project_number=project_number, user_id=user_id))

    return render_template('user_grades_table_for_viewer.html', title='Оценки участника',
                           grades=grades, user=user, project_number=project_number,
                           ParName=parameters, user_id=user_id, len=len(parameters),
                           back=url_for('main.viewer_users_table', project_number=project_number))


# табллца экспертов для наблюдателя
@bp.route('/viewer_experts_table/<project_number>', methods=['GET', 'POST'])
@login_required
def viewer_experts_table(project_number):
    if current_user.id <= 1100000 or current_user.id > 1200000:
        return redirects()
    viewer = Viewer.query.filter_by(id=current_user.id).first()
    project = Project.query.filter_by(number=project_number).first()
    parameters = project.parameters.all()

    return render_template('viewer_experts_table.html', title='Эксперты', viewer=viewer,
                           ParName=parameters, project_number=project_number, project=project,
                           back=url_for('main.viewer_settings', project_number=project_number))


# страница для создания нового проекта
@bp.route('/viewer/create_project', methods=['GET', 'POST'])
@login_required
def create_project():
    if current_user.id <= 1100000 or current_user.id > 1200000:
        return redirects()
    viewer = Viewer.query.filter_by(id=current_user.id).first()
    lvl = 0
    delete_project = False
    if request.method == 'POST':
        result = request.form
        lvl = 0
        delete_project = False
        try:
            if request.files['logo'] and request.files['users'] \
                    and request.files['experts'] and request.files.getlist("users_photo") \
                    and request.files.getlist("experts_photo") and result.get('start') \
                    and result.get('end') and result.get('name'):

                project = Project(viewer_id=current_user.id, name=result.get('name'))
                db.session.add(project)
                db.session.commit()
                delete_project = True
                project = Project.query.all()[-1]

                for i in range(int(result.get('quantity'))):
                    db.session.add(Parameter(name=result.get('name{}'.format(i)),
                                             weight=result.get('weight{}'.format(i)),
                                             project_number=project.number))

                start = result.get('start')
                setattr(project, 'start', datetime.strptime(start, '%d.%m.%y'))
                end = result.get('end')
                setattr(project, 'end', datetime.strptime(end, '%d.%m.%y'))
                db.session.commit()

                os.chdir("app/static/images")
                lvl += 3
                if os.path.exists('{}'.format(project.number)):
                    shutil.rmtree('{}'.format(project.number))
                os.mkdir('{}'.format(project.number))
                os.chdir('{}'.format(project.number))
                lvl += 1

                logo = request.files['logo']
                logo.save(os.path.join(os.getcwd(), '{}.png'.format(project.number)))

                users = request.files['users']
                users.filename = secure_filename_2(users.filename.rsplit(" ", 1)[0])
                users.save(secure_filename_2(users.filename.rsplit(".", 1)[0]))
                excel_user(users.filename, project.number)

                experts = request.files['experts']
                experts.filename = secure_filename_2(experts.filename.rsplit(" ", 1)[0])
                experts.save(secure_filename_2(experts.filename.rsplit(".", 1)[0]))
                excel_expert(experts.filename.rsplit(".", 1)[0], project.number)

                def async_mail_expert(ap, project_number):
                    engine = create_engine("sqlite:////var/www/fastuser/data/www/rating.nspt.ru/T_Park.db")
                    with ap.app_context():
                        experts = Expert.query.filter_by(project_number=project_number).all()
                        for expert in experts:
                            passw = password_generator()
                            engine.execute("UPDATE expert SET password_hash = ? WHERE email = ?",
                                           generate_password_hash(passw), expert.email)
                            msg = Message('NSPT Ваш пароль', sender=current_app.config['MAIL_USERNAME'],
                                          recipients=[expert.email])
                            msg.body = render_template('email/send_password.txt',
                                                       user=expert, password=passw)
                            msg.html = render_template('email/send_password.html',
                                                       user=expert, password=passw)
                            mail.send(msg)

                        users = User.query.filter_by(project_number=project_number).all()
                        for user in users:
                            passw = password_generator()
                            engine.execute("UPDATE user SET password_hash = ? WHERE email = ?",
                                           generate_password_hash(passw), user.email)
                            msg = Message('NSPT Ваш пароль', sender=current_app.config['MAIL_USERNAME'],
                                          recipients=[user.email])
                            msg.body = render_template('email/send_password.txt',
                                                       user=user, password=passw)
                            msg.html = render_template('email/send_password.html',
                                                       user=user, password=passw)
                            mail.send(msg)


                def experts_mail(project_number):
                    from main import app as ap
                    Thread(target=async_mail_expert,
                           args=(ap, project_number)).start()

                experts_mail(project.number)
                os.mkdir('users')
                os.mkdir('experts')
                users_photo = request.files.getlist("users_photo")
                experts_photo = request.files.getlist("experts_photo")
                os.chdir('users')
                lvl += 1
                for photo in users_photo:
                    photo.save(os.path.join(os.getcwd(), '{}.png').format(photo.filename.rsplit(".", 1)[0]))
                    compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(photo.filename.rsplit(".", 1)[0])))
                os.chdir('../experts')

                for photo in experts_photo:
                    photo.save(os.path.join(os.getcwd(), '{}.png').format(photo.filename.rsplit(".", 1)[0]))
                    compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(photo.filename.rsplit(".", 1)[0])))

                db.session.commit()
                os.chdir('../../../../../')
                lvl = 0
                flash('Проект создан', 'success')
                return redirect(url_for('main.viewer', viewer_id=current_user.id))
            else:
                flash('Ошибка создания проекта. '
                      'Пожалуйста проверьте, чтобы все поля были заполнены '
                      'и удалите пустые критерии.', 'danger')
                db.session.rollback()
                return redirect(url_for('main.create_project', viewer_id=current_user.id))
        except:
            for i in range(lvl):
                os.chdir('../')
            flash('Что-то пошло не так. Попробуйте снова.', 'danger')
            db.session.rollback()
            if delete_project:
                project = Project.query.all()[-1]
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
            return redirect(url_for('main.create_project'))

    return render_template('create_project.html', title='Создание проекта', back=url_for('main.viewer'))


# добавление участника
@bp.route('/add_new_user/<project_number>', methods=['GET', 'POST'])
@login_required
def add_new_user(project_number):
    if current_user.id <= 1100000:
        return redirects()

    if request.method == 'POST':
        result = request.form

        if result.get('username') and result.get('email') and \
                result.get('birthday') != 'дд.мм.гггг':
            if User.query.filter_by(email=result.get('email')).first() is None:
                last_user_id = User.query.filter_by(project_number=project_number).all()[-1].project_id
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

                if request.files['photo']:
                    os.chdir("app/static/images/{}/users".format(project_number))
                    try:
                        photo = request.files['photo']
                        photo.save(os.path.join(os.getcwd(), '{}.png').format(last_user_id + 1))
                        compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(last_user_id + 1)))
                    except:
                        pass
                    os.chdir('../../../../../')

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
@login_required
def add_new_expert(project_number):
    if current_user.id <= 1100000:
        return redirects()

    if request.method == 'POST':
        result = request.form
        if result.get('username') and result.get('email'):
            if Expert.query.filter_by(email=result.get('email')).first() is None:
                last_expert_id = Expert.query.filter_by(project_number=project_number).all()[-1].project_id
                expert = Expert(project_number=project_number, username=result.get('username'),
                                email=result.get('email'), project_id=last_expert_id + 1)

                db.session.add(expert)
                db.session.commit()

                expert = Expert.query.filter_by(project_number=project_number, project_id=last_expert_id + 1).first()

                if result.get('weight'):
                    setattr(expert, 'weight', result.get('weight'))

                if request.files['photo']:
                    os.chdir("app/static/images/{}/experts".format(project_number))
                    try:
                        photo = request.files['photo']
                        photo.save(os.path.join(os.getcwd(), '{}.png').format(last_expert_id + 1))
                        compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(last_expert_id + 1)))
                    except:
                        pass
                    os.chdir('../../../../../')

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
@login_required
def admin():
    if current_user.id <= 1200000:
        return redirects()
    admin = Admin.query.filter_by(id=current_user.id).first()

    return render_template('admin_main.html', admin=admin)


# страница со всеми проектами
@bp.route('/admin/projects', methods=['GET', 'POST'])
@login_required
def admin_projects():
    if current_user.id <= 1200000:
        return redirects()
    admin = Admin.query.filter_by(id=current_user.id).first()
    projects = Project.query.order_by(Project.start.desc()).all()

    return render_template('admin_projects.html', admin=admin, projects=projects, title='Проекты',
                           back=url_for('main.admin'))


# страница Настройки проектов + доступ к юзерам и экспертам.
@bp.route('/admin/settings/<project_number>', methods=['GET', 'POST'])
@login_required
def admin_settings(project_number):
    if current_user.id <= 1200000:
        return redirects()
    admin = Admin.query.filter_by(id=current_user.id).first()
    project = Project.query.filter_by(number=project_number).first()

    if request.method == 'POST':
        # try:
        result = request.form

        if request.files['users'] and request.files['users_photo']:
            number = User.query.filter_by(project_number=project_number).all()[-1].project_id
            users = request.files['users']
            users.filename = secure_filename_2(users.filename.rsplit(" ", 1)[0])
            users.save(secure_filename_2(users.filename.rsplit(".", 1)[0]))
            excel_user(users.filename, project.number)
            def async_mail_ex(ap, project_number, number):
                engine = create_engine("sqlite:////var/www/fastuser/data/www/rating.nspt.ru/T_Park.db")
                with ap.app_context():
                    users = User.query.filter_by(project_number=project_number).all()
                    for i in range(number):
                        users.pop(0)
                    for user in users:
                        passw = password_generator()
                        engine.execute("UPDATE user SET password_hash = ? WHERE email = ?",
                                       generate_password_hash(passw), user.email)
                        msg = Message('NSPT Ваш пароль', sender=current_app.config['MAIL_USERNAME'],
                                      recipients=[user.email])
                        msg.body = render_template('email/send_password.txt',
                                                   user=user, password=passw)
                        msg.html = render_template('email/send_password.html',
                                                   user=user, password=passw)
                        mail.send(msg)


            def ex_mail(project_number, number):
                from main import app as ap
                Thread(target=async_mail_ex,
                       args=(ap, project_number, number)).start()
            ex_mail(project.number, number)
            users_photo = request.files.getlist("users_photo")
            os.chdir("app/static/images/{}/users".format(project_number))
            for photo in users_photo:
                photo.save(os.path.join(os.getcwd(), '{}.png').format(number + int(photo.filename.rsplit(".", 1)[0])))
                compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(number + int(photo.filename.rsplit(".", 1)[0]))))
                number += 1
            os.chdir('../../../../../')


        if request.files['experts'] and request.files['experts_photo']:
            number = Expert.query.filter_by(project_number=project_number).all()[-1].project_id
            experts = request.files['experts']
            experts.filename = secure_filename_2(experts.filename.rsplit(" ", 1)[0])
            experts.save(secure_filename_2(experts.filename.rsplit(".", 1)[0]))
            excel_expert(experts.filename, project.number)
            experts_photo = request.files.getlist("experts_photo")

            def async_mail_ex_2(ap, project_number, number):
                engine = create_engine("sqlite:////var/www/fastuser/data/www/rating.nspt.ru/T_Park.db")
                with ap.app_context():
                    users = Expert.query.filter_by(project_number=project_number).all()
                    for i in range(number):
                        users.pop(0)

                    for user in users:
                        passw = password_generator()
                        engine.execute("UPDATE expert SET password_hash = ? WHERE email = ?",
                                       generate_password_hash(passw), user.email)
                        msg = Message('NSPT Ваш пароль', sender=current_app.config['MAIL_USERNAME'],
                                      recipients=[user.email])
                        msg.body = render_template('email/send_password.txt',
                                                   user=user, password=passw)
                        msg.html = render_template('email/send_password.html',
                                                   user=user, password=passw)
                        mail.send(msg)


            def ex_mail_2(project_number, number):
                from main import app as ap
                Thread(target=async_mail_ex_2,
                       args=(ap, project_number, number)).start()

            ex_mail_2(project.number, number)

            os.chdir("app/static/images/{}/experts".format(project_number))
            for photo in experts_photo:
                photo.save(os.path.join(os.getcwd(), '{}.png').format(number + 1))
                compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(number + 1)))
                number += 1
            os.chdir('../../../../../')


        if request.files['logo']:
            os.chdir('app/static/images/{}'.format(project_number))
            try:
                logo = request.files['logo']
                logo.save(os.path.join(os.getcwd(), '{}.png'.format(project.number)))
            except:
                pass
            os.chdir('../../../../')

        if result.get('start') and result.get('end') and result.get('name'):
            setattr(project, 'name', result.get('name'))
            setattr(project, 'start', datetime.strptime(result.get('start'), '%d.%m.%y'))
            setattr(project, 'end', datetime.strptime(result.get('end'), '%d.%m.%y'))
        else:
            flash('Мы не смолгли пременить изменения. '
                  'Проверить корректность заполненых полей', 'warning')
            return redirect(url_for('main.admin_settings', project_number=project_number))

        db.session.commit()

        flash('Изменения сохранены', 'success')
        return redirect(url_for('main.admin_settings', project_number=project_number))

    return render_template('admin_settings.html', admin=admin, project=project,
                           back=url_for('main.admin_projects'))


# таблица всех участников из проекта для админа
@bp.route('/admin_users_table/<project_number>', methods=['GET', 'POST'])
@login_required
def admin_users_table(project_number):
    if current_user.id <= 1200000:
        return redirects()
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
@login_required
def admin_experts_table(project_number):
    if current_user.id <= 1200000:
        return redirects()
    admin = Admin.query.filter_by(id=current_user.id).first()
    project = Project.query.filter_by(number=project_number).first()
    parameters = project.parameters.all()

    return render_template('admin_experts_table.html', title='Эксперты', admin=admin,
                           ParName=parameters, project_number=project_number, project=project,
                           back=url_for('main.admin_settings', project_number=project_number))


# страница для выдачи ролей
@bp.route('/admin_waiting_users', methods=['GET', 'POST'])
@login_required
def admin_waiting_users():
    if current_user.id <= 1200000:
        return redirects()

    waiting_users = WaitingUser.query.limit(15)

    return render_template('admin_waiting_users.html', waiting_users=waiting_users,
                           back=url_for('main.admin'))


@bp.route('/admin_viewers', methods=['GET', 'POST'])
@login_required
def admin_viewers():
    if current_user.id <= 1200000:
        return redirects()

    viewers = Viewer.query.limit(10)

    return render_template('admin_viewers.html', viewers=viewers, back=url_for('main.admin'))


# таблица личных оценок участника (для админа)
@bp.route('/user_grades_table_for_admin/<project_number>/<user_id>', methods=['GET', 'POST'])
@login_required
def user_grades_table_for_admin(project_number, user_id):
    if current_user.id <= 1200000:
        return redirects()

    grades = Grade.query.filter_by(user_id=user_id).order_by(Grade.expert_id).limit(20)
    user = User.query.filter_by(id=user_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()

    if request.method == 'POST':
        os.chdir('app/static/images/{}/users'.format(project_number))
        try:
            old_img = os.path.join(os.getcwd(), '{}.png'.format(user.project_id))
            if os.path.exists(old_img):
                os.remove(old_img)
            img = request.files['photo']
            img.save(os.path.join(os.getcwd(), '{}.png'.format(user.project_id)))
            compression(100, 150, os.path.join(os.getcwd(), '{}.png'.format(user.project_id)))
        except:
            flash('Не удалось сохранить фото', 'warning')
            return redirect(url_for('main.user_grades_for_admin',
                                    project_number=project_number, expert_id=user_id))
        os.chdir('../../../../../')
        flash('Изменения сохранены', 'success')
        return redirect(url_for('main.user_grades_table_for_admin',
                                project_number=project_number, user_id=user_id))

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
            send_role_update(user, 'Администратор')

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
        os.chdir('app/static/images/{}/users'.format(user.project_number))
        try:
            old_img = os.path.join(os.getcwd(), '{}.png'.format(user.project_id))
            if os.path.exists(old_img):
                os.remove(old_img)
        except:
            pass
        os.chdir('../../../../../')

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
        if expert:
            db.session.delete(expert)
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

    if getattr(user, 'team') != data[2].capitalize():
        setattr(user, 'team', data[2].capitalize())

    if getattr(user, 'region') != data[3]:
        setattr(user, 'region', data[3])

    setattr(user, 'birthday', datetime.strptime(data[1], '%Y-%m-%d'))

    db.session.commit()

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
            .order_by(Viewer.project_id).limit(int(request.form['lim']) + 1)

    return jsonify({'viewers': viewers_in_json(viewers)})
