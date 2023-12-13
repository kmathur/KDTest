import os, sys
import logging
from flask import Flask, jsonify, request
import shlex
#from utils import PreProcessing
#import server
import prediction, json
import persist_requests as pr
import logging, traceback, uuid
import appjob
from model import AttachedModel
from bd_vlib3 import *
from pwd import getpwnam

logging.config.fileConfig('bdlog.conf')
setup_logger = logging.getLogger("bluedataLogger")
setup_logger.setLevel(logging.DEBUG)

def serve(req_json, mode='itv'):
    #Load the saved model
    (R, Out) = validateJson(req_json)
    if not R:
        return Out
    if 'model_json' in Out:
        modelJson = req_json['model_json']
    else:
        modelJson = ''
    if 'score_url' in Out:
        score_url = req_json['score_url']
    if 'score_cmd' in Out:
        score_cmd = req_json['score_cmd']
    else:
        score_cmd = ''

    use_scoring = req_json['use_scoring']
    scoring_args = req_json['scoring_args']
    response = None
    try:
       id = pr.create_req(scoring_args, "", 'external')
       setup_logger.info("Created request")
       serve_model = AttachedModel(req_json['model_name'], req_json['model_version'])
       setup_logger.info("GOt serve model")
       cmd = appjob.genSrvCmd(serve_model.scoring, scoring_args, score_cmd, use_scoring)
       setup_logger.info("Done with request")
       setup_logger.info('executing cmd for serving: ' + cmd)
       #exe =  cmd.split() #+ [">", prediction.getRequestLog(id)]
       exe=shlex.split(cmd)
       setup_logger.info("Done with request")
       response_dict = prediction.score(exe, id, mode)
       setup_logger.info("Done with request")
       response_dict['request_url'] = prediction.get_resource_url('/history/' + str(id), 'external')
       return response_dict
    except Exception as e:
        # TODO: currently we return a string. To keep consistency, we need to send an aapropriate JSON.
        # We also need to update the status as Failed if an entry has been made in the DB
        setup_logger.error(str(e))
        return str(e)
    return response

def train(req_json):
    #Validate Training json
    (R, Out) = validateTrainingJson(req_json)
    if not R:
        return Out
    train_code_str = req_json['training_code']
    username = req_json['calledBy']
    setup_logger.info("Executing training code ...")
    setup_logger.info("Got user name: " + username)
    response = None
    try:
        cmd = req_json['training_code']
        code =  cmd.split("\n")
        id = pr.create_req(code, 'Training job submitted')
        deletedId = pr.removeIfFull(id)
        if deletedId != -1:
            (deleted_src, deleted_log) = gen_train_source_log(deletedId)
            prediction.score(["rm", "-f", deleted_src, deleted_log])
            setup_logger.info("deleted training request for id: " + str(deletedId))
        (train_src, train_log) = gen_train_source_log(id)
        os.system('sudo mkdir -vp' + train_src)
        os.system('sudo mkdir -vp' + train_log)
        setup_logger.info("starting training code for training job: " + str(id))
        with open(train_src, "a") as f:
            for line in code:
                f.write(line + "\n")
        with open(train_log, "a") as f:
            pass
        setup_logger.info("created training source job file : " + train_src)
        setup_logger.info("created training source job file on the executing worker: " + pr.get_request_node(id))
        ##Default mode for training Must always be 'batch'
        


        # get UIDs and GIDs
        uid = getpwnam(username)[2]
        gid = getpwnam(username)[3]
        # Change the ownership of train and request files. train_src has the code, while train_log records the logs.
        # Both these files are now assigned the user that gave the magics call.
        os.chown(train_src, uid, gid)
        os.chown(train_log, uid, gid)
        setup_logger.info("Changed the user")

        cmd = "python3 -u -W ignore " + str(train_src) + " > " + str(train_log)
        cmds = shlex.split(cmd)
        setup_logger.info("Split command is : " + str(cmds))
        response_dict = prediction.score(cmds, id, 'batch')
        # We now run python process as a su and specify the user with which we want to run it
        #response_dict = prediction.score(["su", "-c", "'python3 -u -W ignore {} > {}'".format(train_src, train_log), "-", username], id, 'batch')

        response_dict["request_url"] = prediction.get_resource_url('/history/' + str(id))
        return response_dict
    except Exception as e:
        setup_logger.error(str(e))
        return str(e)
    return response

def validateTrainingJson(inputJson):
    try:
        _TrainingCode = inputJson['training_code']
        return (True, '')
    except Exception as e:
        AllowedKeys = [ 'training_code' ]
        KeysFound = inputJson.keys()
        a_b = list(set(KeysFound) - set(AllowedKeys))
        Out = "validation failed with unknown key(s):" + ','.join(a_b)
        setup_logger.error(Out)
        return (False, Out)

def validateJson(inputJson):
    try:
        _Use_scoring = inputJson['use_scoring']
        _Scoring_args = inputJson['scoring_args']
        return (True, inputJson.keys())
    except Exception as e:
        AllowedKeys = ['model_json', 'score_url', 'score_cmd', 'use_scoring', 'scoring_args']
        KeysFound = inputJson.keys()
        a_b = list(set(KeysFound) - set(AllowedKeys))
        Out = "validation failed with unknown key(s):" + ','.join(a_b)
        setup_logger.error(Out)
        return (False, Out)

##To-do
def validate_model_json(model_json):
    return True

def bad_request(error=None):
    message = {
            'status': 400,
            'message': 'Bad Request: ' + request.url + '--> Please check your data payload...',
    }
    resp = jsonify(message)
    resp.status_code = 400
    return resp

def unauthorized(error=None):
    message = {
        'status': 401,
        'message': 'HTTP/1.1 401 Unauthorized'
    }
    resp = jsonify(message)
    resp.status_code = 401
    return resp

def get_all_requests():
    return pr.get_all()

def get_request(id):
    return pr.get_req(id)

def kill_request(id):
    return pr.kill_request(id)

def get_logs(id):
    return {"id" : id,
            "logs" : prediction.readlogs(id)}

# def download_and_unpack(url):
#     wget.download('/tmp', url, extract=True)
def gen_train_source_log(id):
    return (prediction.getClusterHome() + '/train' + str(id),
        prediction.getRequestLog(str(id)))
