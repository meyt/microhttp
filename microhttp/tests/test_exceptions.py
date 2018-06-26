import unittest

from sqlalchemy import MetaData, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from nanohttp import RestController, json, settings, context

from microhttp import Application as BaseApplication
from microhttp.ext import db
from microhttp.tests.helpers import WebTestCase


metadata = MetaData()
DeclarativeBase = declarative_base(metadata=metadata)


class Tag(DeclarativeBase):
    __tablename__ = 'tags'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(120), nullable=False, unique=True)


class TestCase(WebTestCase):

    # noinspection PyAbstractClass
    class Application(BaseApplication):
        class Root(RestController):

            @json
            @db.commit
            def post(self):
                db_session = db.get_session(context.form.get('db_session'))
                tag = Tag()
                if context.form.get('id'):
                    tag.id = context.form.get('id')
                tag.tag = context.form.get('tag')
                db_session.add(tag)
                return dict()

        def __init__(self):
            super().__init__(self.Root())

        def configure(self, *args, **kwargs):
            super().configure(*args, **kwargs)
            settings.merge("""
                sqlalchemy:
                  default:
                    engine:
                      name_or_url: 'sqlite://'
                      echo: False
                    session:
                      autoflush: False
                      autocommit: False
                      expire_on_commit: True
                  db2:
                    admin_db_url: 'postgresql://postgres:postgres@localhost'
                    engine:
                      echo: False
                      name_or_url: 'postgresql://postgres:postgres@localhost/microhttp_demo'
            """)
            db.configure()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with db.get_database_manager('db2') as manager:
            manager.create_database_if_not_exists()

        for _, db_session in db.get_sessions().items():
            metadata.create_all(bind=db_session.get_bind())

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        for _, db_session in db.get_sessions().items():
            db_session.close()
            db_session.get_bind().dispose()

        with db.get_database_manager('db2') as manager:
            manager.drop_database()

    def test_any_exception(self):
        # For all non `nanohttp.HttStatus` exceptions
        self.app.post('/?db_session=default', params=dict(tag='test'), status=200)
        self.app.post('/?db_session=default', params=dict(tag='test'), status=500)

    def test_postgres_exceptions(self):
        self.app.post('/?db_session=db2', params=dict(tag='test'), status=200)

        # unique_violation
        resp = self.app.post('/?db_session=db2', params=dict(tag='test'), status=409)
        self.assertEqual(resp.status, '409 unique_violation')

        # not_null_violation
        resp = self.app.post('/?db_session=db2', status=400)
        self.assertEqual(resp.status, '400 not_null_violation')

        # invalid_text_representation
        resp = self.app.post('/?db_session=db2&id=^', status=400)
        self.assertEqual(resp.status, '400 invalid_text_representation')


if __name__ == '__main__':  # pragma: nocover
    unittest.main()
