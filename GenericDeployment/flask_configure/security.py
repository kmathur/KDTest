import os, logging, sys
logging.config.fileConfig('bdlog.conf')
setup_logger = logging.getLogger("bluedataLogger")
setup_logger.setLevel(logging.DEBUG)

class Unauthorized(Exception):
    status_code = 401

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

def authorize(request):
    if request.args.get('auth') == 'none':
        setup_logger.info("Internal request no taken required, validation succeded")
        return ""

    req_token = request.headers.get('X-Auth-Token')
    setup_logger.info("Token: {0}".format(req_token))
    if req_token:
        setup_logger.info("Authorizing token:" +str(req_token))
        token = os.popen("bdvcli -g services.haproxy.1.LoadBalancer.authToken").read().rstrip()
        setup_logger.info("bd_vcli token: {0}".format(token))
        if req_token != token:
             raise Unauthorized("HTTP/1.1 401 Unauthorized")
        else:
            return ""
    else:
        raise Unauthorized("HTTP/1.1 401 Unauthorized: Token not found")
