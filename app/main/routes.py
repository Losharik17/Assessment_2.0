import json
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app, send_file
from flask_login import current_user, login_required
from app import db
from app.main.forms import EmptyForm, GradeForm, UserForm
from app.models import User, Expert, Grade, Viewer, Admin, Parameter
from app.main import bp
from app.main.functions import users_in_json, grades_in_json, excel, to_dict, delete_timer, redirects
import pandas as pd
from werkzeug.utils import secure_filename


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/T-Park', methods=['GET', 'POST'])
def index():
    return render_template('base.html', auth=current_user.is_authenticated)


@bp.route('/download')
@login_required
def dwn():
    """if current_user.id <= 11000:
        return redirects()"""
    return render_template('download.html')


@bp.route('/excel', methods=['GET', 'POST'])
@login_required
def export_excel():
    """if current_user.id <= 11000:
        return redirects()"""
    data = User.query.all()
    data_list = [to_dict(item) for item in data]
    df1 = pd.DataFrame(data_list)
    df1 = df1.drop(columns=['password_hash', 'project_id', 'project_number'])
    rows = Parameter.query.count()
    row = Parameter.query.filter_by(project_number=1).first()
    i = row.id
    f = 1
    for i in range(i, rows+1):
        parameter = Parameter.query.filter_by(id = i).first()
        df1.rename(columns={df1.columns[f + 5]: parameter.name}, inplace=True)
        f += 1 # 5 - это костыль, но позиция sum_grade_0 у нас вроде как постоянная поэтому менять пока не буду
    df1.rename(columns={'sum_grade_all': 'Сумма критериев', 'username': 'ФИО',
                        'birthday': 'Дата рождения', "team": "Команда",
                        "place": "Регион", "id": "ID"}, inplace=True)
    df1 = df1.fillna('-')
    # df1 = df1.loc[df1['project_number'].isin(1)]"
    data = Expert.query.all()
    data_list = [to_dict(item) for item in data]
    df2 = pd.DataFrame(data_list)
    df2 = df2.drop(columns=['password_hash', 'project_id', 'project_number', 'quantity'])
    df2.rename(columns={'username':'ФИО', 'weight':'Вес', 'id':'ID'}, inplace=True)
    data = Grade.query.all()
    data_list = [to_dict(item) for item in data]
    df3 = pd.DataFrame(data_list)
    df3 = df3.drop(columns=['id'])
    df3.rename(columns={'user_id': 'ID пользователя', 'expert_id': 'ID эксперта',
                        'date': 'Дата выставления оценки', 'comment':'Комментарий'}, inplace=True)
    f = 1
    i = row.id
    for i in range(i, rows+1):
        parameter = Parameter.query.filter_by(id = i).first()
        df3.rename(columns={df3.columns[f + 2]: parameter.name}, inplace=True) # 2 - то же самое, что и 5
        f += 1
    filename = "/Отчёт.xlsx"

    writer = pd.ExcelWriter(filename, date_format='dd/mm/yyyy', datetime_format='dd/mm/yyyy hh:mm', engine='xlsxwriter')
    df1.to_excel(writer, sheet_name='Пользователи', index=False, float_format="%.1f")
    workbook = writer.book
    new_format = workbook.add_format({'align': 'center'})  #pip install xlsxwriter - надо установить, чтобы заработало, если нет, то хз если честн, у меня всё робит
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


@bp.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    """if current_user.id <= 11000:
        return redirects()"""
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
    """if current_user.id <= 10000 and current_user.id != user.id:
        return redirects()"""
    return render_template('user.html', user=user)


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
            flash('None User')
            return redirect(url_for('main.expert', expert_id=current_user.id))
        return redirect(url_for('main.expert_grade', project_number=project_number,
                                expert_id=current_user.id, user_id=user.id))
    return render_template('expert.html', form=form, expert=expert)


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

        flash('Text')
        return redirect(url_for('main.expert', project_number=project_number,
                                expert_id=current_user.id))

    user = User.query.filter_by(id=user_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()

    if (user.project_number == Expert.query.filter_by(id=current_user.id).first().project_number):
        pass
    return render_template('expert_grade.html', form=form, expert_id=current_user.id,
                           user=user, parameters=parameters, project_number=project_number)


# главня страница наблюдателя
@bp.route('/viewer/<viewer_id>', methods=['GET', 'POST'])
@login_required
def viewer(viewer_id):
    if current_user.id <= 11000:
        return redirects()
    viewer = Viewer.query.filter_by(viewer_id=viewer_id).first()
    return render_template('viewer.html', viever=viewer)


# главная страница админа
@bp.route('/admin/<admin_id>', methods=['GET', 'POST'])
@login_required
def admin(admin_id):
    """if current_user.id <= 11000:
        return redirects()"""
    admin = Admin.query.filter_by(id=admin_id).first()
    return render_template('admin.html', admin=admin)


# таблица всех участников из проекта
@bp.route('/admin_table/<project_number>/<admin_id>', methods=['GET', 'POST'])
@login_required
def admin_table(project_number, admin_id):
    """if current_user.id <= 11000:
        return redirects()"""
    admin = Admin.query.filter_by(id=admin_id).first()
    parameters = Parameter.query.filter_by(project_number=project_number).all()
    users = User.query.filter_by(project_number=project_number).order_by(User.id).limit(5)
    return render_template('admin_table.html', title='Table', admin=admin,
                           users=users, ParName=parameters, project_number=project_number)


# таблица личных оценок участника (для админа)
@bp.route('/user_grades_table/<project_number>/<user_id>', methods=['GET', 'POST'])
@login_required
def user_grades_table(project_number, user_id):
    """if current_user.id <= 11000:
        return redirects()"""
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


# delete_timer()