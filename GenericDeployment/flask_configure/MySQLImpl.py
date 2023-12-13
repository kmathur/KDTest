import mysql.connector
import DBConstants
import uuid
from DBUtils import AbstractDB
from typing import Dict, Optional, Any, List, Tuple


class MySQLConnectionManager:
    """
    Connection Manager for MySQL Database. The class shall create and flush connection
    """

    def __init__(self, config: Dict[str, str]):
        """
        Initialize with a config dictionary
        :param config:
        """
        self.config = config

    def __enter__(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            return self.connection
        except Exception as e:
            raise Exception("Error creating connection in MySQLConnectionManager [{}]".format(e))

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


class MySQLImpl(AbstractDB):
    logger = None

    def __init__(self, config):
        self.config = config

    def _create(self, table_name: str, table_specs: str) -> None:
        """
        Creates a table if it is not present
        :param table_name: table name
        :param table_specs: specification

        Sample call: _create(t1, <specifications>)
        Corresponding SQL query: CREATE TABLE IF NOT EXISTS `t1` (<specifications>);
        """
        prep_statement = "CREATE TABLE IF NOT EXISTS `{}` ({})".format(table_name, table_specs)
        self._execute_query(False, prep_statement)

    def _delete(self, table_name: str, params=None) -> None:
        """
        Deletes the input table
        :param table_name: table to be deleted
        :param params: None expected

        Sample call: _delete(t1)
        Corresponding SQL query: DROP TABLE IF EXISTS `t1`;
        """
        prep_statement = "DROP TABLE IF EXISTS `{}`".format(table_name)
        self._execute_query(False, prep_statement)

    def _execute_query(self, fetch_result: bool = False, *args):
        """
        Executes a query by getting a connection object and returns a result set if it is required.
        :param fetch_result: Does the query need to fetch result set?
        :param args: Query to be executed
        :return: None / List

        """
        result = None
        with MySQLConnectionManager(self.config) as connection:
            cursor = connection.cursor()
            cursor.execute(*args)
            if fetch_result:
                result = cursor.fetchall()
            connection.commit()
        return result

    def update(self,
               tables: List,
               clause: str,
               where: Optional[str] = "",
               params: Optional[str] = "") -> None:
        """
        Updates table(s) with corresponding values based on the input condition.
        :param tables: List of tables to update
        :param clause: The values are to be set
        :param where: Condition expression for UPDATE
        :param params: Parameters like LOW_PRIORITY, IGNORE, ...

        Sample call: update([t1], clause = "name={}".format(name), where="id = {}".format(id))
        Corresponding SQL query: UPDATE t1 SET name=<name> WHERE id=<id>;
        """

        if not where:
            prep_statement = "UPDATE {} {} SET {}".format(params, ', '.join(tables), clause)
        else:
            prep_statement = "UPDATE {} {} SET {} WHERE {}".format(params, ', '.join(tables), clause, where)
        self._execute_query(False, prep_statement)

    def insert(self,
               table: str,
               params: Optional[str] = "",
               col_dict: Dict[str, Any] = dict()) -> None:
        """
        Inserts one row into the specified table
        :param table: table to insert row into
        :param params: Parameters like LOW_PRIORITY, DELAY, ...
        :param col_dict: A dictionary of the form {col_name: col_value}

        Sample call: insert(t1, row) row={'id':<id>, ...}
        Corresponding SQL query: INSERT INTO t1(row.keys) VALUES (row.values);
        """
        columns = col_dict.keys()
        prep_statement = "INSERT {} INTO {}({})".format(params, table, ', '.join(columns))
        prep_statement = prep_statement + " VALUES({})".format(', '.join(["%s"] * len(col_dict)))
        self._execute_query(False, prep_statement, list(col_dict.values()))

    def search(self,
               table: str,
               columns: List = list(),
               where: Optional[str] = "") -> List[Tuple[Any]]:
        """
        Search and return the query result
        :param table: query table
        :param columns: list of columns to return
        :param where: Optional condition expression for SEARCH
        :return: A list of tuples, where every tuple corresponds to a row

        Sample call: search(t1,columns=["node"], where="id = {}".format(id))
        Corresponding SQL query: SELECT node FROM t1 WHERE id=<id>;
        """
        if not where:
            prep_statement = "SELECT {} FROM {}".format(", ".join(columns), table)
        else:
            prep_statement = "SELECT {} FROM {} WHERE {}".format(", ".join(columns), table, where)
        return self._execute_query(True, prep_statement)

    def remove(self,
               tables: List[str],
               clause: str,
               params: Optional[str] = "") -> None:
        """
        Removes rows from a list of tables which satisfy a condition

        :param tables: List of tables
        :param clause: the condition for removal
        :param params: Optional parameters like LOW_PRIORITY, DELAY, ...

        Sample call: remove([t1], clause="WHERE node={}".format(nodeToRemove))
        Corresponding SQL query: DELETE FROM t1 WHERE node=<nodeToRemove>;
        """
        prep_statement = "DELETE {} FROM {}  {} ".format(params, ', '.join(tables), clause)
        self._execute_query(False, prep_statement)


def test_impl():
    """
    Sample test implementation. Can be removed.
    """
    row = {
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["INPUT"]: "data/test_data.npy data/test_label.npy",
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT[
            "LOG_URL"]: "logs_url",
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["NODE"]: "node",
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT[
            "OUTPUT"]: "\nLoading test data\nLoaded test data\nLoaded PCA model\nLoaded kNN  model. Now predicting ...\nAccuracy for kNN model is:  0.9723\nAccuracy for kNN model is:  97.23\n\n",
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["PID"]: 1406,
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["STATUS"]: DBConstants.JOB_STATUS.Finished.name,
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["UUID"]: str(uuid.uuid4())
    }

    try:
        sql = MySQLImpl(DBConstants.MYSQL_ENDPOINT_TABLE_CONFIG)
        sql._create(DBConstants.MYSQL_ENDPOINT_TABLE_NAME, DBConstants.MYSQL_ENDPOINT_TABLE_CREATE)
        sql.insert(DBConstants.MYSQL_ENDPOINT_TABLE_NAME, col_dict=row)
        # sql.remove([DBConstants.MYSQL_ENDPOINT_TABLE_NAME],
        #            "WHERE {}=1".format(DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["ID"]))
        #
        res = sql.search(DBConstants.MYSQL_ENDPOINT_TABLE_NAME, ["*"])
        # where="{}>=1".format(DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["ID"]))
        for rrow in res:
            print(rrow)
        # sql.update([DBConstants.MYSQL_ENDPOINT_TABLE_NAME], "input='{}' where qid={}".format(
        # "changed_from_connector", 1))
        # sql.update([DBConstants.MYSQL_ENDPOINT_TABLE_NAME], "input='{}'".format(
        # "changed_from_connector_2"), where="qid={}".format(1))
    except Exception as e:
        print(e)

    sql = MySQLImpl(DBConstants.MYSQL_ENDPOINT_TABLE_CONFIG)
    uid = uuid.uuid4()
    row = {
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["INPUT"]: "data/test_data.npy data/test_label.npy",
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["NODE"]: "node",
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["STATUS"]: "Finished",
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT[
            "OUTPUT"]: "\nLoading test data\nLoaded test data\nLoaded PCA model\nLoaded kNN  model. Now predicting "
                       "...\nAccuracy for kNN model is:  0.9723\nAccuracy for kNN model is:  97.23\n\n",
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["UUID"]: str(uid)
    }

    sql.insert(DBConstants.MYSQL_ENDPOINT_TABLE_NAME, col_dict=row)

    qid = sql.search(DBConstants.MYSQL_ENDPOINT_TABLE_NAME,
                     [DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["ID"]],
                     where="{}='{}'".format(DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["UUID"], str(uid)))[0][0]

    print(qid)
    log_url = "logs_url" + str(qid)
    sql.update([DBConstants.MYSQL_ENDPOINT_TABLE_NAME],
               "{}='{}'".format(DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["LOG_URL"], log_url),
               where="{}={}".format(DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["ID"], qid))
    res = sql.search(DBConstants.MYSQL_ENDPOINT_TABLE_NAME, ["*"])
    for r in res:
        print(r)

# test_impl()
