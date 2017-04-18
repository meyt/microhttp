from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker, session as sa_session
from microhttp import bus
from nanohttp import settings
from typing import Dict
import functools


def configure():
    bus.ext.db.sessions = {}
    for db_alias, db_spec in settings.sqlalchemy.items():
        sa_engine = create_engine(**db_spec['engine'])
        db_spec['session']['bind'] = sa_engine
        bus.ext.db.sessions[db_alias] = scoped_session(sessionmaker(**db_spec['session']))


def get_sessions() -> Dict[str, sa_session.Session]:
    return bus.ext.db.sessions


def get_session(session_name) -> sa_session.Session:
    return bus.ext.db.sessions[session_name]


def drop_all(metadata, sessions_list=None):
    sessions_list = sessions_list or bus.ext.db.sessions.keys()
    for session in sessions_list:
        metadata.drop_all(bind=bus.ext.db.sessions[session].bind)


def commit(func):
    """
    Commit Decorator
    Notice: Use it before nanohttp:action family decorators like template.render.
    :param func: 
    :return: 
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        def commit_all_sessions():
            for session_alias, session in bus.ext.db.sessions.items():
                try:
                    session.commit()
                except:
                    session.rollback()
                    raise
        try:
            result = func(*args, **kwargs)
            commit_all_sessions()
            return result
        except exc.StatementError:
            commit_all_sessions()
    return wrapper
