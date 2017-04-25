import unittest

from nanohttp import Controller, html, InternalServerError

from microhttp import Application as BaseApplication
from microhttp.ext import db
from microhttp.tests.helpers import WebTestCase


class TestCase(WebTestCase):

    class Application(BaseApplication):
        class Root(Controller):
            @html
            def index(self):
                db_session = db.get_session('db1')
                try:
                    db_session.execute('SELECT * FROM sqlite_master')
                    return ''
                except:
                    raise InternalServerError

        def __init__(self):
            self.builtin_configuration += """
sqlalchemy:
  db1:
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

if __name__ == '__main__':
    unittest.main()
