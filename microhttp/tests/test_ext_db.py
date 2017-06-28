import unittest

from nanohttp import Controller, html, HttpInternalServerError

from microhttp import Application as BaseApplication
from microhttp.ext import db
from microhttp.tests.helpers import WebTestCase


class TestCase(WebTestCase):

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
            self.builtin_configuration += """
sqlalchemy:
  default:
    engine:
      name_or_url: 'sqlite:///:memory:'
      echo: false
    session:
      autoflush: True
      autocommit: False
      expire_on_commit: True
  db2:
    engine:
      name_or_url: 'sqlite:///:memory:'
      echo: false
    session:
      autoflush: True
      autocommit: False
      expire_on_commit: True
            """
            super().__init__(self.Root())

        def prepare(self):
            db.configure()

    def test_simple(self):
        resp = self.app.get('/')
        assert resp.status_int == 200

    def test_another_database(self):
        resp = self.app.get('/db2')
        assert resp.status_int == 200

if __name__ == '__main__':
    unittest.main()
