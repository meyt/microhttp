microhttp
=========

.. image:: https://img.shields.io/pypi/pyversions/microhttp.svg
    :target: https://pypi.python.org/pypi/microhttp

.. image:: https://travis-ci.org/meyt/microhttp.svg?branch=master
    :target: https://travis-ci.org/meyt/microhttp

.. image:: https://coveralls.io/repos/github/meyt/microhttp/badge.svg?branch=master
    :target: https://coveralls.io/github/meyt/microhttp?branch=master

A tool-chain for web applications based on `nanohttp <https://github.com/pylover/nanohttp>`_.


Default supported extensions:

- db - Database support (using `sqlalchemy <https://www.sqlalchemy.org>`_)
- template - Template support (using `mako <http://www.makotemplates.org/>`_)
- session - Session management (using `dogpile.cache <https://dogpilecache.readthedocs.io/>`_)
- log - Python builtin logging wrapper
- i18n - Internationalization support with builtin ``gettext``
- email - ``SMTP`` wrapper for sending emails
