#!/usr/bin/env python
from datetime import datetime, timedelta
import unittest
from app import create_app, db
from app.models import User, Expert, Grade
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_big(self):
        u1 = User(username='one', email='a@t.ry')
        u2 = User(username='two', email='b@t.ry')
        u1.set_password('123')
        u2.set_password('123')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        e1 = Expert(username='dima')
        db.session.add(e1)
        db.session.commit()

        g1 = Grade(user_id=u2.id, expert_id=e1.id)
        g1.parameter_0 = -1
        g1.parameter_1 = 3

        g2 = Grade(user_id=u2.id, expert_id=e1.id)
        g2.parameter_0 = -1
        g2.parameter_1 = 3

        db.session.add_all([g1, g2])
        db.session.commit()

        grades = Grade.query.filter_by(user_id=u2.id).all()

        self.assertFalse(int(g1.expert_id) != int(e1.id))
        self.assertTrue(int(g1.expert_id) == int(e1.id))


if __name__ == '__main__':
    unittest.main(verbosity=2)
