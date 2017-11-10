import mock
import unittest

from nanohttp import Controller, html, HttpInternalServerError, settings

from microhttp import Application as BaseApplication
from microhttp.ext import db
from microhttp.tests.helpers import WebTestCase


class TestCase(WebTestCase):

    # noinspection PyAbstractClass
    class Application(BaseApplication):
        class Root(Controller):
            @html
            def index(self):
                db_session = db.get_session()
                try:
                    db_session.execute('SELECT * FROM sqlite_master')
                    return ''
                except:
                    raise HttpInternalServerError

            @html
            def db2(self):
                db_session = db.get_session('db2')
                try:
                    db_session.execute('SELECT * FROM sqlite_master')
                    return ''
                except:
                    raise HttpInternalServerError

        def __init__(self):
            super().__init__(self.Root())

        def configure(self, *args, **kwargs):
            super().configure(*args, **kwargs)
            settings.merge("""
                sqlalchemy:
                  default:
                    engine:
                      name_or_url: 'sqlite:///%(microhttp_dir)s/tests/stuff/default.db'
                      echo: false
                    session:
                      autoflush: True
                      autocommit: False
                      expire_on_commit: True
                  db2:
                    engine:
                      name_or_url: 'sqlite:///%(microhttp_dir)s/tests/stuff/db2.db'
                      echo: false
                    session:
                      autoflush: True
                      autocommit: False
                      expire_on_commit: True
                  db3:
                    admin_db_url: 'mysql+pymysql://john:doe@somehost'
                    engine:
                      name_or_url: 'mysql+pymysql://scott:tiger@somehost/xyz'
                  db4:
                    admin_db_url: 'postgresql://john:doe@localhost'
                    engine:
                      name_or_url: 'postgresql://scott:tiger@localhost/postgres'
            """)
            db.configure()

    def setUp(self):
        super().setUp()
        with db.get_database_manager() as manager:
            manager.create_database_if_not_exists()

        with db.get_database_manager('db2') as manager:
            manager.create_database_if_not_exists()

    def tearDown(self):
        super().tearDown()
        with db.get_database_manager() as manager:
            manager.drop_database()

        with db.get_database_manager('db2') as manager:
            manager.drop_database()

    def test_simple(self):
        resp = self.app.get('/')
        assert resp.status_int == 200

    def test_another_database(self):
        resp = self.app.get('/db2')
        assert resp.status_int == 200

    @mock.patch('microhttp.ext.db.database_manager.create_engine')
    def test_database_manager(self, *_):
        with self.assertRaises(RuntimeError):
            with db.get_database_manager('db2') as manager:
                manager.create_database()
                manager.create_database()
                manager.drop_database()

        with db.get_database_manager('db3') as manager:
            manager.create_database_if_not_exists()
            manager.create_database()
            manager.drop_database()

        with db.get_database_manager('db4') as manager:
            manager.create_database_if_not_exists()
            manager.create_database()
            manager.drop_database()

        settings.sqlalchemy.db4.engine.name_or_url = 'access:///'
        with self.assertRaises(ValueError):
            with db.get_database_manager('db4'):
                pass

if __name__ == '__main__':  # pragma: nocover
    unittest.main()
