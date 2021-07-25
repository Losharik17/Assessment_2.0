from app import db
from app.models import User, Expert, Viewer, Admin
import pandas as pd
from sqlalchemy import create_engine

def users_in_json(users):

    string = '['
    for user in users:
        string += '{"id":' + str(user.id) + ',"username":"' + str(user.username) + \
                  '","birthday":"' + str(user.birthday) + '","team":"' + str(user.team) + \
                  '",'
        for i in range(5):
            string += '"sum_grade_{}":'.format(i) + \
                      str(user.__dict__['sum_grade_{}'.format(i)]) + ','
        string += '"sum_grade_all":' + str(user.sum_grade_all) + '},'

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
        x = db.session.query(Model).delete()
        db.session.commit()
    except:
        db.session.rollback()



def excell(filename):
    df = pd.read_excel(filename)
    engine = create_engine("sqlite:///T_park.db")
    df.head
    if filename == 'user':
        delete(User)
        df.columns = ['id', 'username', 'email', 'avatar', 'password_hash', 'birth_date', 'team']
        df.to_sql(filename, con=engine, if_exists='append', index=False)
    elif filename == 'admin':
        delete(Admin)
        df.columns = ['admin_id', 'username', 'email']
        df.to_sql(filename, con=engine, if_exists='append', index=False)
    elif filename == 'expert':
        delete(Expert)
        df.columns = ['id', 'username', 'email', 'weight', 'quantity']
        df.to_sql(filename, con=engine, if_exists='append', index=False)
    elif filename == 'viewer':
        delete(Viewer)
        df.columns = ['id', 'username', 'email']
        df.to_sql(filename, con=engine, if_exists='append', index=False)
    else:
        print('Неправильно выбран файл')