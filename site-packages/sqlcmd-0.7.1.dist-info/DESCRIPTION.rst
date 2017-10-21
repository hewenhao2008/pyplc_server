*sqlcmd* is a SQL command line tool, similar in concept to tools like Oracle's
`SQL*Plus`_, the PostgreSQL_ ``psql`` command, and MySQL_'s ``mysql`` tool.

.. _SQL*Plus: http://www.oracle.com/technology/docs/tech/sql_plus/index.html
.. _PostgreSQL: http://www.postgresql.org/
.. _MySQL: http://www.mysql.org/

Some features at a glance
--------------------------

- Connection parameters for individual databases are kept in a configuration
  file in your home directory.
- Databases can be assigned multiple logical names.
- *sqlcmd* has command history management, with `GNU Readline`_ support.
  History files are saved per database.
- *sqlcmd* supports SQL, but also supports database metadata (getting a list
  of tables, querying the table's columns and their data types, listing the
  indexes and foreign keys for a table, etc.).
- *sqlcmd* supports Unix shell-style variables.
- *sqlcmd* command has a ``.set`` command that displays and controls *sqlcmd*
  settings.
- *sqlcmd* provides a standard interface that works the same no matter what
  database you're using.
- *sqlcmd* uses the enhanced database drivers in the `Grizzled API`_'s ``db``
  module. (Those drivers are, in turn, built on top of standard Python
  DB API drivers like ``psycopg2`` and ``MySQLdb``.)
- *sqlcmd* is written entirely in `Python`_, which makes it very portable
  (though the database drivers are often written in C and may not be available
  on all platforms).

.. _Grizzled API: http://www.clapper.org/software/python/grizzled/
.. _GNU Readline: http://cnswww.cns.cwru.edu/php/chet/readline/rluserman.html
.. _Python: http://www.python.org/

In short, *sqlcmd* is a SQL command tool that attempts to provide the same
interface for all supported databases and across all platforms.


