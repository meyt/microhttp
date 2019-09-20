from pytest import fixture

from sqlalchemy import MetaData, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from nanohttp import RestController, json, settings, context

from microhttp import Application
from microhttp.ext import db


metadata = MetaData()
DeclarativeBase = declarative_base(metadata=metadata)

app_configuration = """
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
            name_or_url: 'postgresql://postgres:postgres@localhost/microhttpd'
"""


class Tag(DeclarativeBase):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(120), nullable=False, unique=True)


class DemoApplication(Application):
    class Root(RestController):
        @json
        @db.commit
        def post(self):
            db_session = db.get_session(context.form.get("db_session"))
            tag = Tag()
            if context.form.get("id"):
                tag.id = context.form.get("id")
            tag.tag = context.form.get("tag")
            db_session.add(tag)
            return dict()

    def __init__(self):
        super().__init__(self.Root())

    def configure(self, *args, **kwargs):
        super().configure(*args, **kwargs)
        settings.merge(app_configuration)
        db.configure()


@fixture(scope="module")
def app(webtest):
    webtest.setup_application(DemoApplication)
    with db.get_database_manager("db2") as manager:
        manager.create_database_if_not_exists()

    for _, db_session in db.get_sessions().items():
        metadata.create_all(bind=db_session.get_bind())

    yield webtest.app

    for _, db_session in db.get_sessions().items():
        db_session.close()
        db_session.get_bind().dispose()

    with db.get_database_manager("db2") as manager:
        manager.drop_database()


def test_any_exception(app):
    # For all non `nanohttp.HttStatus` exceptions
    app.post("/?db_session=default", params=dict(tag="test"), status=200)
    app.post("/?db_session=default", params=dict(tag="test"), status=500)


def test_postgres_exceptions(app):
    app.post("/?db_session=db2", params=dict(tag="test"), status=200)

    # unique_violation
    resp = app.post("/?db_session=db2", params=dict(tag="test"), status=409)
    assert resp.status == "409 unique_violation"

    # not_null_violation
    resp = app.post("/?db_session=db2", status=400)
    assert resp.status == "400 not_null_violation"

    # invalid_text_representation
    resp = app.post("/?db_session=db2&id=^", status=400)
    assert resp.status == "400 invalid_text_representation"
