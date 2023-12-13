import re
import base64
import logging
import sys
from bd_vlib3 import *

notebook_logger = logging.getLogger("ConfigCli Ops")
notebook_logger.setLevel(logging.DEBUG)
hdlr = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
hdlr.setFormatter(formatter)
hdlr.setLevel(logging.DEBUG)
notebook_logger.addHandler(hdlr)

"""
This class is intended to get token values from configmeta.json specifically for Secrets. 
The values can be got as decoded or encoded strings.
No error is thrown upon an incorrect key, rather None is returned 
"""


class ConfigCliOps(object):

    def __init__(self, *args, **kwargs):
        #configcli = ConfigCli(shell=False)
        self.ConfigMeta = BDVLIB_ConfigMetadata()
        self.DECODE_BASE = "base64"
        self.SERVICES = "services"
        self.AUTH_TOKEN = "authToken"

    def get_with_tokens(self, jsonpath, decode=False):
        try:
            result = self.ConfigMeta.getWithTokens(jsonpath)
            return self.decode_token(result) if decode else result
        except Exception as e:
            notebook_logger.error(
                "Exception occured while getting token for " + str(jsonpath))
            notebook_logger.error(e)
            notebook_logger.error("Returning None")
            return None

    def decode_token(self, bytesData):
        return bytesData.decode(self.DECODE_BASE).strip()

    def search_for_token(self, jsonpath, search_str):
        try:
            return self.ConfigMeta.searchForToken(jsonpath, search_str)
        except Exception as e:
            notebook_logger.error(
                "Exception occured while searching token " + str(jsonpath) + " :" + str(search_str))
            notebook_logger.error(e)
            notebook_logger.error("Returning None")
            return None

    def service_auth_token(self, service, role, node_id="1"):
        auth_token_path = [self.SERVICES, service,
                           node_id, role, self.AUTH_TOKEN]
        return self.get_with_tokens(auth_token_path)


configcliops = ConfigCliOps()


"""
ConnectionConfigCliOps extends ConfigCliOps to perform connection-specific operations.
It reads the JSON object from the path that is provided to it in the constructor and stores that object as its attribute
get_with_tokens() called on the instance of this class would apply on this JSON object.

Every connection object will require a separate instance of this class since one instance shall have a fixed JSON object that is traversed
"""
class ConnectionConfigCliOps(ConfigCliOps):
    """
    connectionpath: Path to get the connection JSON object
    index: The object to fetch out the array. Currently only one is assumed. If all the objects are to be considered, index=None
    """
    def __init__(self, connectionpath, index=0, *args, **kwargs):
        super(ConnectionConfigCliOps, self).__init__(*args, **kwargs)
        self.CONNECTION_PATH = connectionpath
        self.INDEX = index
        self.JSON_OBJECT = self.get_json_object(
            self.CONNECTION_PATH, self.INDEX)

    """
    Fetch the JSON object from the parent get_with_tokens method
    """
    def get_json_object(self, connpath, index=None):
        return super(ConnectionConfigCliOps, self).get_with_tokens(connpath)[index] if index is not None else super(ConnectionConfigCliOps, self).get_with_tokens(connpath)

    """
    jsonpath: The path to get the attribute from JSON_OBJECT. The format is same as ConfigMeta.getWithTokens()
    decode: Object is decoded using parent methods
    """
    def get_with_tokens(self, jsonpath=[], decode=False):
        try:
            json_obj = self.JSON_OBJECT
            for item in jsonpath:
                json_obj = json_obj[item]
            return super(ConnectionConfigCliOps, self).decode_token(json_obj) if decode else json_obj
        except Exception as e:
            notebook_logger.error(
                "Exception occured while getting token for " + str(jsonpath))
            notebook_logger.error(e)
            notebook_logger.error("Returning None")
            return None    

    def __str__(self):
        return str(self.JSON_OBJECT)
