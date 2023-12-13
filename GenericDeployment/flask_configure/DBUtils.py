class AbstractDB:
    """
    Acts as a guidance class for the methods that are expected in the database-specific implementation.
    The implementation classes are expected to inherit this class and override appropriate methods.
    """

    def __init__(self):
        return

    def init_logger(self):
        """
        Initialize logger for the class
        :return: None
        """
        return

    def _create(self, query, params):
        """
        Create a new table in the database. It is a hidden method since we do not intend to use this too often from
        the client
        :param query: Query string similar to a prepared statement
        :param params: Parameters to the Query string
        :return: None
        """
        return

    def _delete(self, query, params):
        """
        Delete a table. It is a hidden method since we do not intend to use this too often from
        the client
        :param query: Query string similar to a prepared statement
        :param params: Parameters to the Query string
        :return: None
        """
        return

    def get_count(self, query, params):
        """
        Returns the count of a query.
        :param query: Query string similar to a prepared statement
        :param params: Parameters to the Query
        :return: Number
        """
        return

    def update(self, query, params):
        """
        Update a table column(s) with values.
        :param query: Query string similar to a prepared statement
        :param params: Parameters to the Query string
        :return: None
        """
        return

    def insert(self, query, params):
        """
        Insert row(s) into the table
        :param query: Query string similar to a prepared statement
        :param params: Parameters to the Query string
        :return: None
        """
        return

    def search(self, query, params):
        """
        Run a SELECT query over a table
        :param query: Query string similar to a prepared statement
        :param params: Parameters to the Query string
        :return: A list/tuple depending on the implementation
        """
        return

    def remove(self, query, params):
        """
        Remove row(s) from table(s)
        :param query: Query string similar to a prepared statement
        :param params: Parameters to the Query string
        :return: None
        """
        return
