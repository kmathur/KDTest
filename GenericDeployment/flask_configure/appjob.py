import os, sys
import logging, traceback, uuid
import prediction
import json
from bd_vlib3 import *

setup_logger = logging.getLogger("bluedataLogger")
setup_logger.setLevel(logging.DEBUG)
hdlr = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
hdlr.setFormatter(formatter)
hdlr.setLevel(logging.DEBUG)
setup_logger.addHandler(hdlr)

def genSrvCmd(scoring_script, scoring_args, score_cmd, use_scoring=True):
    scoring_par = "{'ml_engine': 'python'}"#BDVLIB_ConfigMetadata().getWithTokens(["nodegroups", "1", "config_metadata"])
    if 'scoring_prefix' in scoring_par:
        scoring_par = BDVLIB_ConfigMetadata().getWithTokens(["nodegroups", "1", "config_metadata", "scoring_prefix"])
        cmd = ' '.join([scoring_par, scoring_script, scoring_args])
        setup_logger.info("command for scoring engine: " + cmd)
        return cmd
    if use_scoring:
        engine = "python3" #findScoringEngine()
        cmd = ''
        scoring_args = conv_to_dict(scoring_args)
        if engine in ['spark', 'sparkr', 'pyspark']:
            #spark_submit = "sudo -u spark spark-submit --deploy-mode cluster --master yarn"
            spark_submit = "sudo -u spark /usr/hdp/current/spark2-client/bin/spark-submit --master yarn --deploy-mode cluster"
            cmd = ' '.join([spark_submit, scoring_script, scoring_args])
        elif engine == "python":
            #-u for continously writing unbuffered output to file
            cmd = ' '.join(["export TF_CPP_MIN_LOG_LEVEL=2;python3 -u -W ignore", scoring_script, scoring_args])
        elif engine == "python3":
            #cmd = ' '.join(["export TF_CPP_MIN_LOG_LEVEL=2;python3 -u -W ignore", scoring_script, scoring_args])
            cmd = ' '.join(["python3 -u -W ignore", scoring_script, scoring_args])
        else:
            cmd = ' '.join(["export TF_CPP_MIN_LOG_LEVEL=2;python3", scoring_script, scoring_args])
        setup_logger.info("command for scoring engine: " + cmd)
        return cmd
    else:
        return ' '.join([score_cmd, scoring_args])

def findScoringEngine():
    ##Hacky bdvcli again
    ##FIX ME
    try:
        #ml_engine = os.popen('bdvcli --get nodegroups.1.config_metadata.ml_engine').read().rstrip().split(',')[0]
        #eng = os.popen(cmd).read().rstrip()
        ml_engine = BDVLIB_ConfigMetadata().getWithTokens(
            ["nodegroups", "1", "config_metadata", "ml_engine"])
        if ml_engine == 'undefined':
            setup_logger.warning('ml_engine not found, defaulting to python3')
            return 'python3'
        return ml_engine
    except Exception as e:
        setup_logger.error("unable to find engine, defaulting to pyton3")
        return 'python3'

def conv_to_dict(obj):
    if type(obj) is dict:
        setup_logger.info("Input json found for scoring script..")
        return '\'' + json.dumps(obj) + '\''
    return obj