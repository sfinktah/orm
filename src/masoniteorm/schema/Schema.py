from ..connections.ConnectionFactory import ConnectionFactory
from .Blueprint import Blueprint
from .Table import Table
from .TableDiff import TableDiff


class Schema:

    _default_string_length = "255"

    def __init__(
        self,
        dry=False,
        connection=None,
        platform=None,
        grammar=None,
        connection_details={},
        connection_driver=None,
    ):
        self._dry = dry
        self.connection = connection
        self._connection = None
        self.grammar = grammar
        self.platform = platform
        self.connection_details = connection_details
        self._connection_driver = connection_driver

        if not self.platform:
            self.platform = connection.get_default_platform()

    def on(self, connection):
        """Change the connection from the default connection

        Arguments:
            connection {string} -- A connection string like 'mysql' or 'mssql'.
                It will be made with the connection factory.

        Returns:
            cls
        """
        if connection == "default":
            connection = self.connection_details.get("default")

        self._connection_driver = self.connection_details.get(connection).get("driver")

        self.connection = ConnectionFactory().make(self._connection_driver)

        return self

    def dry(self):
        """Change the connection from the default connection

        Arguments:
            connection {string} -- A connection string like 'mysql' or 'mssql'.
                It will be made with the connection factory.

        Returns:
            cls
        """
        self._dry = True
        return self

    def create(self, table):
        """Sets the table and returns the blueprint.

        This should be used as a context manager.

        Arguments:
            table {string} -- The name of a table like 'users'

        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        self._table = table

        return Blueprint(
            self.grammar,
            connection=self.new_connection(),
            table=Table(table),
            action="create",
            platform=self.platform,
            default_string_length=self._default_string_length,
            dry=self._dry,
        )

    def table(self, table):
        """Sets the table and returns the blueprint.

        This should be used as a context manager.

        Arguments:
            table {string} -- The name of a table like 'users'

        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        self._table = table
        return Blueprint(
            self.grammar,
            connection=self.new_connection(),
            table=TableDiff(table),
            action="alter",
            platform=self.platform,
            default_string_length=self._default_string_length,
            dry=self._dry,
        )

    def get_connection_information(self):
        return {
            "host": self.connection_details.get(self._connection_driver, {}).get(
                "host"
            ),
            "database": self.connection_details.get(self._connection_driver, {}).get(
                "database"
            ),
            "user": self.connection_details.get(self._connection_driver, {}).get(
                "user"
            ),
            "port": self.connection_details.get(self._connection_driver, {}).get(
                "port"
            ),
            "password": self.connection_details.get(self._connection_driver, {}).get(
                "password"
            ),
            "prefix": self.connection_details.get(self._connection_driver, {}).get(
                "prefix"
            ),
        }

    def new_connection(self):
        if self._dry:
            return

        self._connection = self.connection(
            **self.get_connection_information()
        ).make_connection()

        return self._connection

    def has_column(self, table, column, query_only=False):
        """Checks if the a table has a specific column

        Arguments:
            table {string} -- The name of a table like 'users'

        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        sql = self.platform().compile_column_exists(table, column)

        if self._dry:
            return sql

        return bool(self.new_connection().query(sql, ()))

    @classmethod
    def set_default_string_length(cls, length):
        cls._default_string_length = length
        return cls

    def drop_table(self, table, query_only=False):
        sql = self.platform().compile_drop_table(table)

        if self._dry:
            return sql

        return bool(self.new_connection().query(sql, ()))

    def drop(self, *args, **kwargs):
        return self.drop_table(*args, **kwargs)

    def drop_table_if_exists(self, table, exists=False, query_only=False):
        sql = self.platform().compile_drop_table_if_exists(table)

        if self._dry:
            return sql

        return bool(self.new_connection().query(sql, ()))

    def rename(self, table, new_name):
        sql = self.platform().compile_rename_table(table, new_name)

        if self._dry:
            return sql

        return bool(self.new_connection().query(sql, ()))

    def truncate(self, table):
        sql = self.platform().compile_truncate(table)

        if self._dry:
            return sql

        return bool(self.new_connection().query(sql, ()))

    def has_table(self, table, query_only=False):
        """Checks if the a database has a specific table
        Arguments:
            table {string} -- The name of a table like 'users'
        Returns:
            masonite.orm.blueprint.Blueprint -- The Masonite ORM blueprint object.
        """
        sql = self.platform().compile_table_exists(table, database=self.get_connection_information().get('database'))

        if self._dry:
            return sql

        return bool(self.new_connection().query(sql, ()))
