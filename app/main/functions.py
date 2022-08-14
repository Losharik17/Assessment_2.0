import random
import string

from sqlalchemy import create_engine
from app import db
from app.models import User, Expert, Viewer, Grade
import pandas as pd
from flask import redirect, url_for, flash, send_file
from app.models import User, Expert, Viewer
import pandas as pd
from flask import redirect, url_for, flash
from apscheduler.schedulers.background import BackgroundScheduler
from flask_login import current_user
import PIL
from PIL import Image
from datetime import datetime, timedelta
from app.models import Project
from app.auth.email import send_alert_mail, send_role_refuse
import os
import shutil
from datetime import date, datetime
import re

engine = create_engine("sqlite:///T_Park.db")


def users_in_json(users):
    if not users:
        return '[]'
    lenght = len(Project.query.filter_by(number=users[0].project_number).first().parameters.all())

    string = '['
    for user in users:

        if user.birthday:
            birthday = user.birthday
        else:
            birthday = '-'
        string += '{' + '"id":{0},"username":"{1}","birthday":"{2}","team":"{3}",' \
                        '"project_number":{4}, "project_id":{5},"region":"{6}",' \
            .format(str(user.id), str(user.username), str(birthday),
                    str(user.team), str(user.project_number),
                    str(user.project_id), str(user.region))

        for i in range(lenght):
            string += '"sum_grade_{0}":"{1}",' \
                .format(i, str(user.__dict__['sum_grade_{}'.format(i)]))

        string += '"sum_grade_all":"{0}"'.format(str(user.sum_grade_all)) + '},'

    string = string[:len(string) - 1] + ']'

    return string


def viewers_in_json(viewers):
    if not viewers:
        return '[]'

    string = '['
    for viewer in viewers:
        string += '{' + '"id":{0},"username":"{1}","phone_number":"{2}","expert_id":"{3}",' \
                        '"email":"{4}"' \
            .format(str(viewer.id), str(viewer.username), str(viewer.phone_number),
                    str(viewer.expert_id), str(viewer.email))

        string += '},'

    string = string[:len(string) - 1] + ']'

    return string


def experts_in_json(experts):
    if not experts:
        return '[]'
    string = '['

    for expert in experts:
        string += '{' + '"id":{0},"username":"{1}","weight":"{2}","quantity":"{3}",' \
                        '"project_number":{4}, "project_id":{5}' \
            .format(str(expert.id),
                    str(expert.username),
                    str(expert.weight),
                    str(expert.quantity),
                    str(expert.project_number),
                    str(expert.project_id)) + '},'

    string = string[:len(string) - 1] + ']'
    return string


def grades_in_json(grades, lenght):
    if not grades:
        return '[]'

    string = '['
    for grade in grades:

        string += '{' + '"id":{0},"date":"{1}","expert_id":"{2}","user_id":"{3}",' \
                        '"comment":"{4}", "username":"{5}", "expertname":"{6}"' \
            .format(str(grade.id),
                    str(grade.date.strftime('%H:%M %d.%m.%y')),
                    str(grade.expert.project_id),
                    str(grade.user.project_id),
                    str(grade.comment), str(grade.user.username),
                    str(grade.expert.username))

        for i in range(lenght):
            string += ',"parameter_{0}":"{1}"' \
                .format(i, str(grade.__dict__['parameter_{}'.format(i)]))

        string += '},'

    string = string[:len(string) - 1] + ']'
    string = string.replace("\r", "").replace("\n", "")

    return string


def waiting_users_in_json(waiting_users):
    if not waiting_users:
        return '[]'
    string = '['
    for waiting_user in waiting_users:
        string += '{' + '"id":{0},"registration_date":"{1}","email":"{2}","username":"{3}",' \
                        '"phone_number":"{4}", "organization":"{5}"' \
            .format(str(waiting_user.id),
                    str(waiting_user.registration_date.strftime('%H:%M %d.%m.%y')),
                    str(waiting_user.email),
                    str(waiting_user.username),
                    str(waiting_user.phone_number),
                    str(waiting_user.organization))
        string += '},'
    string = string[:len(string) - 1] + ']'

    return string


def project_settings(request, project, project_number):
    changes = False
    result = request.form

    if request.files['logo']:
        os.chdir('app/static/images/{}'.format(project_number))
        logo = request.files['logo']
        logo.save(os.path.join(os.getcwd(), 'logo.png'))
        os.chdir('../../../../')
        changes = True

    if result.get('name') != '':
        setattr(project, 'name', result.get('name'))
        changes = True

    if result.get('start') != 'дд.мм.гг':
        setattr(project, 'start', datetime.strptime(result.get('start'), '%d.%m.%y'))
        changes = True
    if result.get('end') != 'дд.мм.гг':
        setattr(project, 'end', datetime.strptime(result.get('end'), '%d.%m.%y'))
        changes = True

    db.session.commit()
    if changes:
        flash('Изменения сохранены', 'success')


def to_dict(row):
    if row is None:
        return None

    rtn_dict = dict()
    keys = row.__table__.columns.keys()
    for key in keys:
        rtn_dict[key] = getattr(row, key)
    return rtn_dict


def delete(Model):
    try:
        db.session.query(Model).delete()
        db.session.commit()
    except:
        db.session.rollback()


def delete_project(project_number):
    db.session.query(User).filter_by(project_number=project_number).delete()
    db.session.query(Expert).filter_by(project_number=project_number).delete()
    db.session.commit()


def password_generator():
    length = 8
    all = string.ascii_letters + string.digits
    password = "".join(random.sample(all, length))
    return password


def excel_user(filename, number):
    df = pd.read_excel(filename)
    df.head
    special_char = ['"', '*', '/', '(', ')', ':', '\n', '.', '!', ',', '-']
    special_char_escaped = list(map(re.escape, special_char))
    df.columns = ['project_id', 'username', 'email', 'birthday', 'team', 'region', 'photo']
    df.applymap(lambda x: x.strip() if type(x)==str else x)
    df['username'] = df['username'].str.strip()
    df['email'] = df['email'].str.lower()
    df['team'] = df['team'].str.capitalize()
    df['region'] = df['region'].str.capitalize()
    df['birthday'] = df['birthday'].dt.date
    df['username'] = df['username'].replace(special_char_escaped, ' ', regex=True)
    df['team'] = df['team'].replace(special_char_escaped, ' ', regex=True)
    df['region'] = df['region'].replace(special_char_escaped, ' ', regex=True)
    prev_user = User.query.filter_by(project_number=number).order_by(User.id.desc()).first()
    last_user = User.query.order_by(User.id.desc()).first()
    index = df.index
    if last_user is not None:
        c = last_user.id
        i = c
        b = len(index) + c
        if prev_user is not None and prev_user.project_number == number:
            l = prev_user.project_id
        else:
            l = 0
    else:
        c = 0
        i = 0
        b = len(index)
        l = 0
    for i in range(i, b):
        df.loc[[i - c]].to_sql('user', con=engine, if_exists='append', index=False)
        user = User.query.filter_by(id=i + 1).first()
        user.project_number = number
        user.set_password(password_generator())
        if user.project_id is None:
            user.project_id = l + 1
        db.session.add(user)
        db.session.commit()
        l += 1


def excel_expert(filename, number):
    df = pd.read_excel(filename)
    df.head
    df.drop = ['photo']
    special_char = ['"', '*', '/', '(', ')', ':', '\n', '.', '!', ',', '-']
    special_char_escaped = list(map(re.escape, special_char))
    df.columns = ['project_id', 'username', 'email', 'weight']
    df.applymap(lambda x: x.strip() if type(x)==str else x)
    df['username'] = df['username'].str.strip()
    df['email'] = df['email'].str.lower()
    df['username'] = df['username'].replace(special_char_escaped, ' ', regex=True)
    prev_expert = Expert.query.filter_by(project_number=number).order_by(Expert.id.desc()).first()
    last_expert = Expert.query.order_by(Expert.id.desc()).first()
    index = df.index
    if last_expert != None:
        i = c = last_expert.id
        b = len(index) + c
        if prev_expert != None and prev_expert.project_number == number:
            l = prev_expert.project_id
        else:
            l = 0
    else:
        c = 0
        i = 0
        l = 0
        b = len(index)
        me = Expert()
        db.session.add(me)
        db.session.commit()
    for i in range(i, b):
        df.loc[[i - c]].to_sql('expert', con=engine, if_exists='append', index=False)
        expert = Expert.query.filter_by(id=i + 1).first()
        if expert.project_id == None:
            expert.project_id = l + 1
        if expert.weight == None:
            expert.weight = 1
        expert.quantity = 0
        expert.project_number = number

        db.session.add(expert)
        db.session.commit()
        l += 1

    me = Expert.query.filter_by(project_id='0').first()
    if me != None:
        db.session.delete(me)
        db.session.commit()


def delete_function():  # Функция для удаления старых данных
    a = engine.execute("SELECT number FROM project WHERE end >= DATE('now', '12 month')")
    a = a.fetchall()
    if a:
        for rows in a:
            b = engine.execute("SELECT id FROM user WHERE project_number = ?", rows[0])
            b = b.fetchall()
            for row in b:
                engine.execute("DELETE FROM grade WHERE user_id = ?", row[0])
            engine.execute("DELETE FROM user WHERE project_number = ?", rows[0])
            engine.execute("DELETE FROM expert WHERE project_number = ?", rows[0])
            engine.execute("DELETE FROM project WHERE number = ?", rows[0])
            os.chdir("app/static/images")
            try:
                if os.path.exists('{}'.format(a)):
                    shutil.rmtree('{}'.format(a))
            except:
                pass
            os.chdir('../../../')


def delete_timer():
    excel = BackgroundScheduler(daemon=True)
    excel.add_job(excel_saver, 'interval', seconds=10)
    excel.start()


def redirects(arg=None):
    if current_user.is_anonymous:
        flash('Авторизируйтесь для получения доступа к странице', 'warning')
        return redirect(url_for('auth.login'))
    if arg is None:
        flash('Извините, у вас нет доступа к данной странице', 'warning')
    if current_user.id < 1000000:
        return redirect(url_for('main.user'))
    if 1000000 < current_user.id < 1100000:
        expert = Expert.query.filter_by(id=current_user.id).first()
        return redirect(url_for('main.expert', project_number=expert.project_number))
    if 1100000 < current_user.id < 1200000:
        return redirect(url_for('main.viewer'))
    if 1200000 < current_user.id:
        return redirect(url_for('main.admin'))


def compression(width, height, path):
    img = Image.open(path)
    img = img.resize((width, height), PIL.Image.ANTIALIAS)
    return img.save(path)


def email_timer():
    from main import app
    with app.app_context():
        projects = Project.query.all()
        month = datetime.now().date() + timedelta(days=30)
        week = datetime.now().date() + timedelta(days=7)
        day = datetime.now().date() + timedelta(days=1)
        for project in projects:
            if project.end == month or project.end == week or project.end == day:
                c = engine.execute("SELECT organization FROM viewer WHERE id = ?", project.viewer_id)
                c = c.fetchall()
                viewer = Viewer.query.filter_by(organization=c[0][0])
                for a in viewer:
                    send_alert_mail(a, project.end, project.name)


def email_saver():
    from main import app
    with app.app_context():
        a = engine.execute("SELECT number FROM project WHERE end == DATE('now', '-1 day')")
        a = a.fetchall()
        for rows in a:
            b = engine.execute("SELECT id FROM user WHERE project_number = ?", rows[0])
            b = b.fetchall()
            for row in b:
                user = User.query.filter_by(id=row[0]).first()
                user.email = user.email + 'λ'
                db.session.add(user)
                db.session.commit()
            c = engine.execute("SELECT id FROM expert WHERE project_number = ?", rows[0])
            c = c.fetchall()
            for row in c:
                expert = Expert.query.filter_by(id=row[0]).first()
                expert.email = expert.email + 'λ'
                db.session.add(expert)
                db.session.commit()

def excel_saver():
    from main import app
    with app.app_context():
        a = engine.execute("SELECT number FROM project")
        a = a.fetchall()
        for project_number in a:
            project_number = project_number[0]
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
                                    'project_id': 'ID'})
            df1["Имя"] = ""
            df1["Фамилия"] = ""
            df1["Отчество"] = ""
            for i in range(0, len(df1.index)):
                try:
                    df1["Имя"][i]=df1["ФИО"][i].split()[1]
                    df1["Фамилия"][i] = df1["ФИО"][i].split()[0]
                    df1["Отчество"][i] = df1["ФИО"][i].split()[2]
                except:
                    pass
            df1 = df1.fillna('-')
            df1 = df1.loc[df1['project_number'] == int(project_number)]
            df1 = df1.drop(columns=['password_hash', 'project_number'])
            names = df1.columns.values
            names_length = len(names)
            new_name = [names[0], names[names_length-2], names[names_length-3],names[names_length-1],names[3], names[2], names[4], names[5], names[6]]
            for i in range(8, names_length-3):
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
            df2["Имя"] = ""
            df2["Фамилия"] = ""
            df2["Отчество"] = ""
            for i in range(0, len(df2.index)):
                try:
                    df2["Фамилия"][i] = df2["ФИО"][i].split()[0]
                    df2["Имя"][i]=df2["ФИО"][i].split()[1]
                    df2["Отчество"][i] = df2["ФИО"][i].split()[2]
                except:
                    pass
            names = df2.columns.values
            names_length = len(names)
            new_name = [names[0],names[names_length-2],names[names_length-3],names[names_length-1],names[2],names[3], names[5], names[6]]
            df2 = df2.reindex(columns=new_name)
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
                    b = engine.execute("SELECT username FROM expert WHERE id = ?", row[0])
                    b = b.fetchall()
                    if c == 0 and int(df3.expert_id[i]) == row[0]:
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
            df3.rename(columns={'user_id': 'ID участника', 'expert_id': 'ФИО эксперта'}, inplace=True)
            df3["Имя"] = ""
            df3["Фамилия"] = ""
            df3["Отчество"] = ""
            for i in range(0, len(df3.index)):
                try:
                    df3["Фамилия"][i] = df3["ФИО эксперта"][i].split()[0]
                    df3["Имя"][i] = df3["ФИО эксперта"][i].split()[1]
                    df3["Отчество"][i] = df3["ФИО эксперта"][i].split()[2]
                except:
                    pass
            names = df3.columns.values
            names_length = len(names)
            new_name = [names[0], names[names_length - 2], names[names_length - 3], names[names_length - 1], names[2]]
            for i in range(3, names_length - 3):
                new_name.append(names[i])
            df3 = df3.reindex(columns=new_name)
            filename = os.path.join(os.getcwd(), "{}.xlsx".format(Project.query.filter_by(number=project_number).first().name))

            writer = pd.ExcelWriter(filename, datetime_format='dd/mm/yyyy hh:mm', engine='xlsxwriter')
            df1.to_excel(writer, sheet_name='Участники', index=False, float_format="%.2f")
            workbook = writer.book
            base_format = workbook.add_format({'align': 'center'})
            new_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'text_wrap': True})
            date_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'num_format': 'dd/mm/yyyy'})
            date2_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'num_format': 'dd/mm/yyyy hh:mm'})
            worksheet = writer.sheets['Участники']

            worksheet.set_column('A:S', 21, base_format)
            worksheet.set_column('F:F', 24, base_format)
            worksheet.set_column('H:H', 26, base_format)
            worksheet.set_column('E:E', 14, date_format)

            df2.to_excel(writer, sheet_name='Эксперты', index=False)
            worksheet = writer.sheets['Эксперты']
            worksheet.set_column('A:G', 21, base_format)
            worksheet.set_column('E:E', 24, base_format)
            worksheet.set_column('G:G', 32, base_format)

            df3.to_excel(writer, sheet_name='Оценки', index=False)
            worksheet = writer.sheets['Оценки']
            worksheet.set_column('A:P', 30, new_format)
            worksheet.set_column('E:E', 24, date2_format)
            writer.save()



