import os, sys
from flask import Flask, jsonify, request

#import server
import flask_wrapper as fw
import prediction, json, security
import logging, traceback, uuid

app = Flask(__name__)
#cache = Cache(app)
setup_logger = logging.getLogger("bluedataLogger")
setup_logger.setLevel(logging.DEBUG)
hdlr = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
hdlr.setFormatter(formatter)
hdlr.setLevel(logging.DEBUG)
setup_logger.addHandler(hdlr)

"""
This snippet is required to capture gunicorn logs
"""
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

@app.route('/<modelname>/<modelversion>/predict', methods=['POST'])
def serve(modelname, modelversion):
    '''
    Authorize token
    '''
    security.authorize(request)
    try:
        req_json = request.get_json()
        req_json['model_name'] = modelname
        req_json['model_version'] = modelversion
        ## Default mode is always batch, if anything other than rela
        ## is chosen then , start in batch mode
        mode = 'batch' if request.args.get('mode') == 'batch' else 'itv'
        setup_logger.info('Received request for serving in mode:' + mode)
        if req_json is None:
            return "error: no input json"
        return jsonify(fw.serve(req_json, mode))
    except Exception as e:
        setup_logger.error('Error: Exception while running ' + str(e))
        return str(e)

@app.route('/train', methods=['POST'])
def train():
    '''
    Authorize token
    '''
    security.authorize(request)
    try:
        req_json = request.get_json()
        setup_logger.info('Received request for training')
        if req_json is None:
            setup_logger.warning('No input json found')
            return "error: no input json"
        return jsonify(fw.train(req_json))
    except Exception as e:
        setup_logger.error('Error: Exception while running ' + str(e))
        return str(e)

@app.route('/history', methods=['GET'])
def get_requests():
    '''
    Authorize token
    '''
    security.authorize(request)
    setup_logger.info("getting all requests ..")
    #return "test"
    return jsonify(fw.get_all_requests())

@app.route('/history/<id>', methods=['GET'])
def get_request(id):
    '''
    Authorize token
    '''
    security.authorize(request)
    setup_logger.info("getting request for id " + str(id))
    return jsonify(fw.get_request(id))

#@app.route('/history/<id>', methods=['DELETE'])
# def kill_request(id):
#     '''
#     Authorize token
#     '''
#     security.authorize(request)
#     setup_logger.info("killing request for id " + str(id))
#     return jsonify(fw.kill_request(id))

@app.route('/logs/<id>', methods=['GET'])
def get_logs(id):
    '''
     Authorize token
    '''
    security.authorize(request)
    setup_logger.info("getting request for id " + str(id))
    return jsonify(fw.get_logs(id))


@app.errorhandler(400)
def bad_request():
    return jsonify(fw.bad_request(error=None))


@app.errorhandler(security.Unauthorized)
def handle_unauthorized_request(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
