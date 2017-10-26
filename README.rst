microhttp
=========

A tool-chain for web applications based on `nanohttp <https://github.com/pylover/nanohttp>`_.


Default supported extensions:

- db - Database support (using `sqlalchemy <https://www.sqlalchemy.org>`_)
- template - Template support (using `mako <http://www.makotemplates.org/>`_)
- session - Session management (using `dogpile.cache <https://dogpilecache.readthedocs.io/>`_)
- recaptcha - Google ReCaptcha [deprecated]
- log - Python builtin logging wrapper
- i18n - Internationalization support with builtin ``gettext``
- email - ``SMTP`` wrapper for sending emails
