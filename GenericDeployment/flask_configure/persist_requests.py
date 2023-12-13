import sys, os, json
import logging.config
import prediction
import uuid
from MySQLImpl import MySQLImpl
from datetime import datetime
import DBConstants

logging.config.fileConfig('bdlog.conf')
setup_logger = logging.getLogger("bluedataLogger")
setup_logger.setLevel(logging.DEBUG)


# setup_logger = logging.getLogger("bluedata_cm_setup")
# setup_logger.setLevel(logging.DEBUG)
# hdlr = logging.StreamHandler(sys.stdout)
# formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
# hdlr.setFormatter(formatter)
# hdlr.setLevel(logging.DEBUG)
# setup_logger.addHandler(hdlr)
# command=os.popen('bdvcli --get project.project_repo')
# ModelLocation=command.read().rstrip()
# DbLocation='/bd-fs-mnt/KartikServing/db/db.json'

def create_req(input_req, output, type=None):
    mysql = get_db()
    uid = uuid.uuid4()
    setup_logger.info("creating serving for uid: " + str(uid))
    row = {
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["INPUT"]: format_string(str(input_req)),
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["NODE"]: prediction.get_remote_node(),
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["STATUS"]: DBConstants.JOB_STATUS.Running.name,
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["OUTPUT"]: format_string(output),
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["UUID"]: str(uid),
        DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["STARTED"]: str(get_current_time())
    }

    mysql.insert(DBConstants.MYSQL_ENDPOINT_TABLE_NAME, col_dict=row)

    qid = mysql.search(DBConstants.MYSQL_ENDPOINT_TABLE_NAME,
                       [DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["ID"]],
                       where="{}='{}'".format(DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["UUID"], str(uid)))[0][0]

    log_url = prediction.get_resource_url('/logs/' + str(qid), type)
    setup_logger.info("LOG URL : " + str(log_url))
    mysql.update([DBConstants.MYSQL_ENDPOINT_TABLE_NAME],
                 "{}='{}'".format(DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["LOG_URL"], log_url),
                 where="{}={}".format(DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["ID"], qid))

    return qid


def update_req(req_id, status, result, time_completed="now"):
    mysql = get_db()
    status = format_string(status)
    result = format_string(result)
    time_completed = str(get_current_time()) if time_completed is "now" else str(time_completed)
    mysql.update([DBConstants.MYSQL_ENDPOINT_TABLE_NAME],
                 "status = '{}', output = '{}', completed = '{}'".format(status, result, time_completed),
                 where="qid = {}".format(req_id))


def update_req_pid(id, pid):
    mysql = get_db()
    mysql.update([DBConstants.MYSQL_ENDPOINT_TABLE_NAME],
                 "pid={}".format(pid),
                 where=" qid = {}".format(id))


def get_all():
    mysql = get_db()
    result = mysql.search(DBConstants.MYSQL_ENDPOINT_TABLE_NAME, ["*"])
    return result


def get_req(req_id):
    mysql = get_db()
    result = mysql.search(DBConstants.MYSQL_ENDPOINT_TABLE_NAME, ["*"], "qid = {}".format(req_id))[0]
    row = dict()
    row[DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["ID"]] = str(result[0])
    row[DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["INPUT"]] = str(result[1])
    row[DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["LOG_URL"]] = str(result[2])
    row[DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["NODE"]] = str(result[3])
    row[DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["OUTPUT"]] = str(result[4])
    row[DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["PID"]] = str(result[5])
    row[DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["STATUS"]] = str(result[6])
    return_list = list()  # some calls from other apps expect an array of JSON objects. So we wrap the dictionary
    # into a list
    return_list.append(row)

    return return_list


def get_request_node(req_id):
    mysql = get_db()
    # req = get_req(req_id)[0]
    # return req['node']
    result = mysql.search(DBConstants.MYSQL_ENDPOINT_TABLE_NAME,
                          [DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["NODE"]],
                          "qid = {}".format(req_id))[0][0]
    return str(result)


def genId(db):
    # we generate ID using the MySQL sequence. this function is no longer needed
    pass


def getDb():
    # the function does not serve any purpose since mysql instance is already created
    pass


def getReqStatus(req_id):
    mysql = get_db()
    setup_logger.info("In getRequestStatus. Got req_id as :  " + str(req_id))

    result = mysql.search(DBConstants.MYSQL_ENDPOINT_TABLE_NAME,
                          [DBConstants.MYSQL_ENDPOINT_TABLE_COL_DICT["STATUS"]],
                          where="qid = {}".format(req_id))[0][0]

    return result


def removeIfFull(id):
    return -1


def kill_request(id):
    subprocess_pid = get_req(id)[0]['pid']
    setup_logger.info('Killing process for this request ...')
    os.kill(subprocess_pid)
    update_req(id, 'Killed', 'this job was killed')
    return 0


def format_string(s):
    return s.replace("'", "''")


def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

g_mysql = None
def get_db():
    global g_mysql

    if g_mysql is None:
        setup_logger.info("Setting up Database connection")
        g_mysql = MySQLImpl(DBConstants.MYSQL_ENDPOINT_TABLE_CONFIG)
        setup_logger.info("Creating tables")
        g_mysql._create(DBConstants.MYSQL_ENDPOINT_TABLE_NAME, DBConstants.MYSQL_ENDPOINT_TABLE_CREATE)
    return g_mysql
