import functools
from typing import Dict

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker, session as sa_session

from nanohttp import settings

from microhttp import bus
from microhttp.ext.db.database_manager import DatabaseManager


def configure():
    bus.ext.db.sessions = {}
    for session_alias, session_spec in settings.sqlalchemy.items():
        sa_engine = create_engine(**session_spec['engine'])
        session_kwargs = dict(session_spec['session']) if 'session' in session_spec else dict()
        session_kwargs['bind'] = sa_engine
        bus.ext.db.sessions[session_alias] = scoped_session(sessionmaker(**session_kwargs))


def get_sessions() -> Dict[str, sa_session.Session]:
    return bus.ext.db.sessions


def get_session(session_alias: str='default') -> sa_session.Session:
    return bus.ext.db.sessions[session_alias]


def get_database_manager(session_alias: str='default') -> DatabaseManager:
    return DatabaseManager(settings.sqlalchemy[session_alias])


def commit_all():
    for session_alias, session in bus.ext.db.sessions.items():
        try:
            session.commit()
        except Exception:
            session.rollback()
            raise


def commit(func):
    """
    Commit Decorator
    :param func:
    :return: 
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            commit_all()
            return result
        except exc.StatementError:
            commit_all()
            raise
    return wrapper
