import subprocess
import threading
import sys
import json
import logging
import logging.config
# import persist_requests as pr
import random
import os
from bd_vlib3 import *
import BDVUtils
from subprocess import Popen, PIPE, STDOUT

logging.config.fileConfig('bdlog.conf')
setup_logger = logging.getLogger("bluedataLogger")
setup_logger.setLevel(logging.DEBUG)


def score(execute_cmd, id, mode='itv'):
    data = {}
    if mode in ['batch', '']:
        thread = threading.Thread(target=run_score, args=(execute_cmd, id, ))
        thread.start()
        #score_async(execute_cmd)
        setup_logger.info('Request submitted: ' + str(id))
        return data
    else:
        return run_score(execute_cmd, id)

def run_score(execute_cmd, id=None):
    import persist_requests as pr  # remove cyclic dependency on persist_request

    try:
        errFile = getRequestLog(id)
        if exec_util(execute_cmd, id, errFile) != -1:
            #pr.update_req(id, "Finished")
            status = "Finished"
        else:
            #pr.update_req(id, "Failed")
            status = "Failed"
        pr.update_req(id, status, readlogs(id))
        data = pr.get_req(str(id))[0]  # get_req returns a list of dictionary
        return data
    except Exception as e:
        setup_logger.error("unable to find scoring file")
        return data

def readlogs(id):
    try:
        with open(getRequestLog(id), 'r') as f:
            setup_logger.info("getting logs for request: " + str(id))
            return f.read()
    except Exception as e:
        setup_logger.error("log file for request not present")
        return ''

#Tail last 20 lines
def taillogs(id):
    try:
        with open(getRequestLog(id), 'r') as f:
            setup_logger.info("tailing logs for request: " + str(id))
            lines = f.readlines()
            if len(lines) > 20:
                return ''.join(lines[len(lines) - 20 : len(lines)])
            return lines
    except Exception as e:
        setup_logger.error("log file for request not present")
        return ''

def stringify(text):
    if isinstance(text, bytes):
        return text.decode('UTF-8').strip()
    return text.strip()

def exec_util(command, id, logFile=None):
    import persist_requests as pr  # remove cyclic dependency on persist_request
    setup_logger.info("THE COMMAND IN EXEC_UTIL: "+ str(command))
    node_id = pr.get_request_node(id)
    setup_logger.info("In exec_util: got node id as :" + str(node_id))
    rn = pr.get_request_node(id)
    setup_logger.info("REQUEST NODE IS: "+ str(rn))
    if not rn:
        setup_logger.info("EXEC LOCAL UTIL")
        exec_local_util(command, id, logFile)
    else:
        setup_logger.info("EXEC REMOTE UTIL")
        #exec_remote_util(command, id, logFile)
        exec_local_util(command, id, logFile)

# Utility to execute shell command
def exec_local_util(command, id=None, logFile=None):
    import persist_requests as pr  # remove cyclic dependency on persist_request
    setup_logger.info("EXECUTING THE COMMAND: "+ str(command))
    try:
        process = subprocess.Popen(command,
            stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        #res = process.communicate()
        if id is not None:
            pr.update_req_pid(id, process.pid)
        output = ''
        err = ''
        while True:
            output = stringify(process.stdout.readline())
            p = output
            #print("output:" + str(output))
            if  output == '' and process.poll() is not None:
                err = stringify(process.stderr.readline())
                if err:
                    #print("err " + str(err))
                    write_log(logFile, str(err) + "\n")
                else:
                    break
            else:
                #print("command running")
                write_log(logFile, str(output) + "\n")
        output = stringify(process.stdout.read())
        write_log(logFile, str(output) + "\n")
        return process.poll()
    except Exception as e:
        setup_logger.error("exception occured while running script")
        #print "caught exception !!"
        write_log(logFile, str(e)+"\n")
        return -1

def exec_remote_util(command, id, logFile=None):
    import persist_requests as pr  # remove cyclic dependency on persist_request
    exe_script = create_tmp_script(command, id)
    remote_command = ['bash', 'remote.sh', pr.get_request_node(id), exe_script, exe_script]
    setup_logger.info("Invoking command on remote host: " + pr.get_request_node(id))
    exec_local_util(remote_command, id, logFile)

#ToDo - REFACTOR, all bdvcli to bdvlib below
##bdvlib not available for python3
##bdvlib cannot be used with python3 yet so this hack
def copyFileRemote(src, dest, node):
    copysrc = ['bdvcli', '--cp', '--node='+node, '--src='+src, '--dest='+dest,'--perms=777']
    exec_local_util(copysrc)


def get_remote_node():
    ParentNodes = [BDVUtils.get_loadbalancer_fqdn()]#os.popen("bdvcli --get_nodegroup_fqdns=1").read().rstrip().split(',')
    idx = random.randint(0, len(ParentNodes) -1)
    ##FIX ME - Currently always go to first node, before productizing add a queue
    setup_logger.info("Executing on compute worker: " + ParentNodes[idx])
    return ParentNodes[idx]

def write_log(logFile, text):
    if logFile is not None:
        with open(logFile, 'a') as fd:
            fd.write(str(text))

def create_tmp_script(cmd, id=random.randint(0, 1000)):
    try:
        script = getClusterHome() + '/request_command' + str(id)
        command = ' '.join(cmd)
        with open(script, 'w+') as f:
            f.write(command)
        os.chmod(script, 0o777)
        setup_logger.info("Tmp script created at : " + script)
        return script
    except Exception as e:
        setup_logger.error('Error: Exception while running ' + str(e))
        return ''

def getProjectRepo():
    #repo = os.popen('mount | grep -o "/bd-fs-mnt/.* type" | tail -1 | head -c -6').read().rstrip()
    repo = '/bd-fs-mnt/project_repo'
    if not repo:
        setup_logger.warning("unable to find, project repo, some history will be lost")
        return '/tmp/'
    return repo

def getCluster():
    cluster = os.popen('bdvcli --get cluster.id').read().rstrip()
    return cluster

def getClusterHome():
    return getProjectRepo() + '/misc/' + getCluster()


def getRequestLog(id):
    return getClusterHome() + '/request' + str(id)


def get_resource_url(resource, type=None):
    ConfigMeta = BDVLIB_ConfigMetadata()
    if type is 'external':
        ## get external endpoints url
        ## Temporary chang efor k8s
        #key = ['services', 'haproxy', '2', 'LoadBalancer', 'external_endpoints']
        #loadbalancer_node = ConfigMeta.getWithTokens(key)[0]
        #return ConfigMeta.getWithTokens(key + [loadbalancer_node]) + resource

        endpoint = BDVUtils.get_external_endpoints()
        setup_logger.info('URL::  ' + str(endpoint))
        return str(endpoint)+ str(resource)

    host = ConfigMeta.getWithTokens(['node', 'fqdn'])
    return 'http://' + host + ':10001' + resource
