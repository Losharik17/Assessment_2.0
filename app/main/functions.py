import random
import string
from sqlalchemy import create_engine
from app import db
from app.auth.email import send_password_mail
from app.models import User, Expert, Viewer, Admin
import pandas as pd
from flask import redirect, url_for, flash
from apscheduler.schedulers.background import BackgroundScheduler
from flask_login import current_user
import PIL
from PIL import Image
from time import time
from datetime import datetime
engine = create_engine("sqlite:///T_park.db")


def users_in_json(users):
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

        for i in range(5):
            string += '"sum_grade_{0}":"{1}",' \
                .format(i, str(user.__dict__['sum_grade_{}'.format(i)]))

        string += '"sum_grade_all":"{0}"'.format(str(user.sum_grade_all)) + '},'

    string = string[:len(string) - 1] + ']'
    return string


def experts_in_json(experts):
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

def grades_in_json(grades):
    string = '['
    for grade in grades:
        string += '{' + '"id":{0},"date":"{1}","expert_id":"{2}","user_id":"{3}",' \
                        '"comment":"{4}"' \
            .format(str(grade.id),
                    str(grade.date.strftime('%H:%M %d.%m.%y')),
                    str(grade.expert_id),
                    str(grade.user_id),
                    str(grade.comment))

        for i in range(5):
            string += ',"parameter_{0}":"{1}"' \
                .format(i, str(grade.__dict__['parameter_{}'.format(i)]))

        string += '},'

    string = string[:len(string) - 1] + ']'
    return string


def waiting_users_in_json(waiting_users):
    string = '['
    for waiting_user in waiting_users:
        string += '{' + '"id":{0},"registration_date":"{1}","email":"{2}","username":"{3}",' \
                        '"phone_number":"{4}"'\
            .format(str(waiting_user.id),
                    str(waiting_user.registration_date.strftime('%H:%M %d.%m.%y')),
                    str(waiting_user.email),
                    str(waiting_user.username),
                    str(waiting_user.phone_number))
        string += '},'
    string = string[:len(string) - 1] + ']'

    return string


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
    l = 0
    df.columns = ['project_id', 'username', 'email', 'birthday', 'team', 'region']
    prev_user = User.query.order_by(User.id.desc()).first()
    index = df.index
    if prev_user != None:
        c = prev_user.id
        i = c
        b = len(index) + c

    else:
        c = 0
        i = 0
        b = len(index)
    for i in range(i, b):
        df.loc[[i - c]].to_sql('user', con=engine, if_exists='append', index=False)
        a = password_generator()
        user = User.query.filter_by(id=i + 1).first()
        if user.project_id == None:
            user.project_id = l + 1
        user.project_number = number
        user.set_password(a)
        db.session.add(user)
        db.session.commit()
        print(a)
        l += 1
        send_password_mail(user, a)


def excel_expert(filename, number):
    df = pd.read_excel(filename)
    df.head
    l = 0
    df.columns = ['project_id', 'username', 'email', 'weight']
    prev_expert = Expert.query.order_by(Expert.id.desc()).first()
    index = df.index
    if prev_expert != None:
        i = c = prev_expert.id
        b = len(index) + c
    else:
        c = 0
        i = 0
        b = len(index)
        me = Expert()
        db.session.add(me)
        db.session.commit()
    for i in range(i, b):
        df.loc[[i - c]].to_sql('expert', con=engine, if_exists='append', index=False)
        a = password_generator()
        expert = Expert.query.filter_by(id=i + 1).first()
        if expert.project_id == None:
            expert.project_id = l + 1
        if expert.weight == None:
            expert.weight = 1
        expert.quantity = 0
        expert.project_number = number
        expert.set_password(a)
        db.session.add(expert)
        db.session.commit()
        l += 1
        send_password_mail(expert, a)
    me = Expert.query.filter_by(project_id='0').first()
    if me != None:
        db.session.delete(me)
        db.session.commit()



def delete_function():
    a = engine.execute("SELECT number FROM project WHERE end_date <= DATE('now', '-1 month')")
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


def delete_timer():
    shed = BackgroundScheduler(daemon=True)
    shed.add_job(delete_function, 'interval', days=1)
    shed.start()


def delete_timer_X():
    shed = BackgroundScheduler(daemon=True)
    shed.add_job(delete_function_X, 'interval', seconds=2)
    shed.start()


y = 9
z = 18

x = 2020

hash_date = datetime(x, y, z)


def delete_function_X():
    a = datetime.now()
    if a >= hash_date:
        print("fs;<FUCK>")


def redirects():
    if current_user.is_anonymous:
        return redirect(url_for('auth.login'))
    if current_user.id < 10000:
        return redirect(url_for('main.user', user_id=current_user.id))
    if 10000 < current_user.id < 11000:
        return redirect(url_for('main.expert', expert_id=current_user.id))
    if 11000 < current_user.id < 12000:
        return redirect(url_for('main.admin', admin_id=current_user.id))
    if 12000 < current_user.id:
        return redirect(url_for('main.viewer', viewer_id=current_user.id))


def compression(width, height, path):
    img = Image.open(path)
    img = img.resize((width, height), PIL.Image.ANTIALIAS)
    return img.save(path)

