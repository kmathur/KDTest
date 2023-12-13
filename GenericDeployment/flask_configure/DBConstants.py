from enum import Enum
from BDVUtils import get_loadbalancer_fqdn


def get_host():
    """
    Function to find the LoadBalancer node name
    :return: Returns the LoadBalancer Node Name
    """

    return get_loadbalancer_fqdn()


MYSQL_USER = "flaskusr"
MYSQL_PASSWORD = "Password12!"
MYSQL_HOST = str(get_host())
MYSQL_DATABASE = "flaskdb"

JOB_STATUS = Enum("JOB_STATUS", "Pending, Running, Finished, Failed")

MYSQL_ENDPOINT_TABLE_NAME = "bd_jobs"
MYSQL_ENDPOINT_TABLE_CREATE = "qid INT UNSIGNED NOT NULL AUTO_INCREMENT, " \
                              "input TEXT, " \
                              "log_url VARCHAR(1000), " \
                              "node VARCHAR(1000) , " \
                              "output TEXT, " \
                              "pid VARCHAR(10), " \
                              "status ENUM ('Pending', 'Running', 'Finished', 'Failed'), " \
                              "uuid VARCHAR(36), " \
                              "primary key (qid), " \
                              "started DATETIME, " \
                              "completed DATETIME"       

MYSQL_ENDPOINT_TABLE_COL_DICT = {
    "ID": "qid",
    "INPUT": "input",
    "LOG_URL": "log_url",
    "NODE": "node",
    "OUTPUT": "output",
    "PID": "pid",
    "STATUS": "status",
    "UUID": "uuid",
    "STARTED": "started",
    "COMPLETED": "completed"
}

MYSQL_ENDPOINT_TABLE_CONFIG = {
    'user': MYSQL_USER,
    'password': MYSQL_PASSWORD,
    'host': MYSQL_HOST,
    'database': MYSQL_DATABASE,
    'raise_on_warnings': False
}
