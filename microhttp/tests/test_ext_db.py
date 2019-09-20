from mock import patch
from pytest import fixture, raises

from sqlalchemy import MetaData, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from nanohttp import (
    Controller,
    html,
    settings,
    HTTPBadRequest,
    HTTPStatus,
    context,
)

from microhttp import Application
from microhttp.ext import db


metadata = MetaData()
DeclarativeBase = declarative_base(metadata=metadata)

app_configuration = """
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
"""


class HTTPNoContent(HTTPStatus):
    status = "204 No Content"

    def render(self):
        result = super().render()
        context.response_content_type = None
        return result


class Tag(DeclarativeBase):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    tag = Column(String(120), nullable=False, unique=True)
    creator = Column(String(120), nullable=False)


class DemoApplication(Application):
    class Root(Controller):
        @html
        def index(self):
            db_session = db.get_session()
            db_session.execute("SELECT * FROM sqlite_master")
            return ""

        @html
        def db2(self):
            db_session = db.get_session("db2")
            db_session.execute("SELECT * FROM sqlite_master")
            return ""

        @html
        @db.commit
        def fail(self):
            db_session = db.get_session("db2")
            tag = Tag()
            tag.tag = "Book"
            tag.creator = "Writer"
            db_session.add(tag)

            tag = Tag()
            tag.tag = "Book"
            tag.creator = "Writer"
            db_session.add(tag)
            return ""

        @html
        def exception(self):
            @db.commit
            def run():
                db_session = db.get_session("db2")
                tag = Tag()
                db_session.add(tag)
                raise HTTPBadRequest("Oh, dementors here!")

            run()

        @html
        @db.commit
        def new_tag(self):
            db_session = db.get_session("db2")
            tag = Tag()
            tag.tag = context.form.get("tag")
            tag.creator = context.form.get("creator")
            db_session.add(tag)
            raise HTTPNoContent

        @html
        def just_commit(self):
            db.commit_all()
            db_session = db.get_session("db2")

            try:
                tag = Tag()
                db_session.add(tag)
                db.commit_all()
            except Exception:
                pass

            return ""

        @html
        def suppress_commit(self):
            context.suppress_db_commit = True
            self.new_tag()

        @html
        def all_sessions(self):
            return ",".join(db.get_sessions().keys())

    def __init__(self):
        super().__init__(self.Root())

    def configure(self, *args, **kwargs):
        super().configure(*args, **kwargs)
        settings.merge(app_configuration)
        db.configure()


@fixture(scope="module")
def app(webtest):
    webtest.setup_application(DemoApplication)
    with db.get_database_manager() as manager:
        manager.create_database_if_not_exists()

    with db.get_database_manager("db2") as manager:
        manager.create_database_if_not_exists()
    metadata.create_all(bind=db.get_session("db2").get_bind())

    yield webtest.app

    with db.get_database_manager() as manager:
        manager.drop_database()

    with db.get_database_manager("db2") as manager:
        manager.drop_database()


def test_simple(app):
    app.get("/", status=200)


def test_fail(app):
    app.get("/fail", status=500)


def test_exception(app):
    app.get("/exception", status=400)
    app.get("/just_commit", status=200)
    # HTTP Success exceptions don't need to rollback
    app.get("/new_tag?tag=Book2&creator=Writer2", status=204)
    db.get_session("db2").query(Tag).filter_by(tag="Book2").one()

    # app.get('/new_tag/fail', status=500)
    app.get("/suppress_commit?tag=Book3&creator=Writer2")
    assert (
        db.get_session("db2").query(Tag).filter_by(tag="Book3").first() is None
    )


def test_all_sessions(app):
    resp = app.get("/all_sessions")
    for session_alias in resp.text.split(","):
        assert session_alias in ("default", "db2", "db3", "db4")


def test_another_database(app):
    app.get("/db2", status=200)


def test_database_manager(app, monkeypatch):
    with patch("microhttp.ext.db.database_manager.create_engine"):
        with raises(RuntimeError):
            with db.get_database_manager("db2") as manager:
                manager.create_database()

        with db.get_database_manager("db3") as manager:
            manager.create_database_if_not_exists()
            manager.create_database()
            manager.drop_database()

        with db.get_database_manager("db4") as manager:
            manager.create_database_if_not_exists()
            manager.create_database()
            manager.drop_database()

        settings.sqlalchemy.db4.engine.name_or_url = "access:///"
        with raises(ValueError):
            db.get_database_manager("db4").__enter__()
