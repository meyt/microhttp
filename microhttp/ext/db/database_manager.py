
import os
from os.path import exists
from urllib.parse import urlparse

from sqlalchemy import create_engine


class AbstractDatabaseManager(object):
    """
    Abstract class of database manager
    """

    def __init__(self, session_spec):
        self.db_url = session_spec.engine.name_or_url
        self.db_name = urlparse(self.db_url).path.lstrip('/')
        # For databases does not require (or have) any administrative system
        if hasattr(session_spec, 'admin_db_url'):
            self.admin_url = session_spec.admin_db_url
            self.admin_db_name = urlparse(self.admin_url).path.lstrip('/')

    def __enter__(self):
        if hasattr(self, 'admin_url'):
            self.engine = create_engine(self.admin_url)
            self.connection = self.engine.connect()
            self.connection.execute('commit')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'admin_url'):
            self.connection.close()
            self.engine.dispose()

    def create_database_if_not_exists(self):
        if not self.database_exists():
            self.create_database()

    def database_exists(self):  # pragma: no cover
        raise NotImplementedError()

    def create_database(self):  # pragma: no cover
        raise NotImplementedError()

    def drop_database(self):  # pragma: no cover
        raise NotImplementedError()


class MysqlManager(AbstractDatabaseManager):
    """ 
    MySQL database manager 
    """

    def __enter__(self):
        super().__enter__()
        self.connection.execute('commit')
        return self

    def database_exists(self):
        r = self.connection.execute('SHOW DATABASES LIKE \'%s\'' % self.db_name)
        try:
            ret = r.cursor.fetchall()
            return len(ret) > 0
        finally:
            r.cursor.close()

    def create_database(self):
        self.connection.execute('CREATE DATABASE %s' % self.db_name)
        self.connection.execute('commit')

    def drop_database(self):
        self.connection.execute('DROP DATABASE IF EXISTS %s' % self.db_name)
        self.connection.execute('commit')


class PostgresManager(AbstractDatabaseManager):
    """ 
    Postgres database manager 
    """

    def __enter__(self):
        super().__enter__()
        self.connection.execute('commit')
        return self

    def database_exists(self):
        r = self.connection.execute('SELECT 1 FROM pg_database WHERE datname = \'%s\'' % self.db_name)
        try:
            ret = r.cursor.fetchall()
            return ret
        finally:
            r.cursor.close()

    def create_database(self):
        self.connection.execute('CREATE DATABASE %s' % self.db_name)
        self.connection.execute('commit')

    def drop_database(self):
        self.connection.execute('DROP DATABASE IF EXISTS %s' % self.db_name)
        self.connection.execute('commit')


class SqliteManager(AbstractDatabaseManager):
    """ 
    SQLite database manager
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = self.db_url.replace('sqlite:///', '')

    def database_exists(self):
        return exists(self.filename)

    def create_database(self):
        if self.database_exists():
            raise RuntimeError('The file is already exists: %s' % self.filename)
        print('Creating: %s' % self.filename)
        open(self.filename, 'a').close()

    def drop_database(self):
        print('Removing: %s' % self.filename)
        os.remove(self.filename)


# noinspection PyAbstractClass
class DatabaseManager(AbstractDatabaseManager):
    """ 
    Some operations to manage database (inside of database system).
    """

    def __new__(cls, session_spec):
        url = session_spec.engine.name_or_url
        if url.startswith('sqlite'):
            manager_class = SqliteManager
        elif url.startswith('postgres'):
            manager_class = PostgresManager
        elif url.startswith('mysql'):
            manager_class = MysqlManager
        else:
            raise ValueError('Unsupported database uri: %s' % url)

        return manager_class(session_spec=session_spec)
