"""
    Dogpile.cache Based Session Management
    Usage:
    >>>    with get_session() as s:
    >>>        s['counter'] = s.get('counter', 0) + 1
    >>>        print(s['counter'])
    
"""

from nanohttp import settings, context
from microhttp import bus
from datetime import datetime


class DogpileCacheSession:
    region = None
    _session = {}
    _session_id = ''

    def __init__(self):
        from dogpile.cache import make_region
        self.region = make_region().configure(**settings.session.dogpile)

    @staticmethod
    def make_session_id():
        import uuid
        return '%s:%s' % (int(datetime.now().timestamp()), uuid.uuid4().hex)

    def get(self, item, default=None):
        return self._session[item] if item in self._session else default

    def __delitem__(self, key):
        del self._session[key]

    def __setitem__(self, key, value):
        self._session[key] = value

    def __getitem__(self, item):
        return self._session[item]

    def __contains__(self, item):
        return item in self._session

    def __enter__(self):
        self._session = {}
        if settings.session.cookie_name in context.cookies:
            self._session_id = context.cookies[settings.session.cookie_name].value
        else:
            self._session_id = self.make_session_id()
            context.cookies[settings.session.cookie_name] = self._session_id
            context.cookies[settings.session.cookie_name]['httponly'] = True
        tmp = self.region.get(self._session_id)
        if isinstance(tmp, dict):
            self._session = tmp
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.region.set(self._session_id, self._session)

    def clear(self):  # pragma:nocover # TODO
        pass


def configure():
    bus.ext.session = DogpileCacheSession()


def get_session() -> DogpileCacheSession:
    return bus.ext.session
