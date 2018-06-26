import mock
import unittest

from sqlalchemy import MetaData, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from nanohttp import Controller, html, settings, HttpBadRequest, HttpStatus, context

from microhttp import Application as BaseApplication
from microhttp.ext import db
from microhttp.tests.helpers import WebTestCase


metadata = MetaData()
DeclarativeBase = declarative_base(metadata=metadata)


class HttpNoContent(HttpStatus):
    status = '204 No Content'

    def render(self):
        result = super().render()
        context.response_content_type = None
        return result


class Tag(DeclarativeBase):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(120), nullable=False, unique=True)
    creator = Column(String(120), nullable=False)


class TestCase(WebTestCase):

    # noinspection PyAbstractClass
    class Application(BaseApplication):
        class Root(Controller):
            @html
            def index(self):
                db_session = db.get_session()
                db_session.execute('SELECT * FROM sqlite_master')
                return ''

            @html
            def db2(self):
                db_session = db.get_session('db2')
                db_session.execute('SELECT * FROM sqlite_master')
                return ''

            @html
            @db.commit
            def new(self):
                db_session = db.get_session('db2')
                db_session.execute("""
                    CREATE TABLE BOOKS ( title TEXT NOT NULL, publication_date TEXT)
                """)
                return ''

            @html
            @db.commit
            def fail(self):
                db_session = db.get_session('db2')
                tag = Tag()
                tag.tag = 'Book'
                tag.creator = 'Writer'
                db_session.add(tag)

                tag = Tag()
                tag.tag = 'Book'
                tag.creator = 'Writer'
                db_session.add(tag)
                return ''

            @html
            def exception(self):
                @db.commit
                def run():
                    db_session = db.get_session('db2')
                    tag = Tag()
                    db_session.add(tag)
                    raise HttpBadRequest('Oh, dementors here!')
                run()

            @html
            @db.commit
            def http_success(self, fail: str=None):
                db_session = db.get_session('db2')
                tag = Tag()
                tag.tag = 'Book2'
                tag.creator = 'Writer2'
                db_session.add(tag)

                if fail is not None:
                    tag = Tag()
                    tag.tag = 'Book2'
                    tag.creator = 'Writer2'
                    db_session.add(tag)

                raise HttpNoContent

            @html
            def just_commit(self):
                db.commit_all()
                db_session = db.get_session('db2')

                try:
                    tag = Tag()
                    db_session.add(tag)
                    db.commit_all()
                except Exception:
                    pass

                return ''

            @html
            def all_sessions(self):
                return ','.join(db.get_sessions().keys())

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
                      autoflush: False
                      autocommit: False
                      expire_on_commit: True
                      twophase: False

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
        metadata.create_all(bind=db.get_session('db2').get_bind())

    def tearDown(self):
        super().tearDown()
        with db.get_database_manager() as manager:
            manager.drop_database()

        with db.get_database_manager('db2') as manager:
            manager.drop_database()

    def test_simple(self):
        self.app.get('/', status=200)

    def test_fail(self):
        self.app.get('/fail', status=500)

    def test_exception(self):
        self.app.get('/exception', status=400)
        self.app.get('/just_commit', status=200)
        # HTTP Success exceptions don't need to rollback
        self.app.get('/http_success', status=204)
        db.get_session('db2').query(Tag).filter_by(tag='Book2').one()

        self.app.get('/http_success/fail', status=500)

    def test_all_sessions(self):
        resp = self.app.get('/all_sessions')
        for session_alias in resp.text.split(','):
            self.assertTrue(session_alias, ['default', 'db2', 'db3', 'db4'])

    def test_another_database(self):
        self.app.get('/db2', status=200)

    def test_new(self):
        self.app.get('/new', status=200)

    @mock.patch('microhttp.ext.db.database_manager.create_engine')
    def test_database_manager(self, *_):
        with self.assertRaises(RuntimeError):
            with db.get_database_manager('db2') as manager:
                manager.create_database()

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
            db.get_database_manager('db4').__enter__()


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
