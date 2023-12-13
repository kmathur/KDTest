import logging
import traceback
import uuid
from ConfigCliOps import configcliops as genericops
from ConfigCliOps import ConnectionConfigCliOps
import logging
import logging.config
import re
logging.config.fileConfig('bdlog.conf')
setup_logger = logging.getLogger("bluedataLogger")
setup_logger.setLevel(logging.DEBUG)

PATH_MODELS = ["connections", "configmaps", "model"]
PATH_DATA = "data"
CONST_SCORING_PATH = "scoring-path"
CONST_PATH = "path"
CONST_NAME = "name"
CONST_MODEL_VERSION = "model-version"

"""
AttachedModel has the following attributes: 
name: model name
version: model version
index: the index of the model in configmeta that matches name and version 
ConnectionConfigMeta: the JSON object corresponding to the index
scoring: path to scoring script
modelpath: path to model
"""
class AttachedModel:
    def __init__(self, name, version):
        self.name = name
        self.version = version
        self.set_index_and_connection_object()
        self.scoring = self.ConnectionConfigMeta.get_with_tokens(
            [PATH_DATA, CONST_SCORING_PATH])
        self.modelpath = self.ConnectionConfigMeta.get_with_tokens(
            [PATH_DATA, CONST_PATH])
        self.scoring = self.convert_path_to_bd_fs_mnt(self.scoring)
        self.modelpath = self.convert_path_to_bd_fs_mnt(self.modelpath)

    """
    set index and ConnectionConfigMeta object.
    Traverse the JSON array and find the matching JSON entry for model name and version.
    Raise an exception if no match is found
    """
    def set_index_and_connection_object(self):
        all_models = genericops.get_with_tokens(PATH_MODELS)
        search_dict = {CONST_NAME: self.name,
                       CONST_MODEL_VERSION: self.version
                       }

        for x in range(len(all_models)):
            if search_dict.items() <= all_models[x][PATH_DATA].items():
                self.index = x
                self.ConnectionConfigMeta = ConnectionConfigCliOps(
                    PATH_MODELS, index=x)
                return

        setup_logger.error("Invalid model name/version")
        raise Exception

    # def nameToId(self, name, version):
    #     ConfigMeta = BDVLIB_ConfigMetadata()
    #     found_models = ConfigMeta.searchForToken("connections", name)
    #     if found_models != []:
    #         for mod in found_models:
    #             #model_path = m[0:3]
    #             #print(mod)
    #             if ConfigMeta.getWithTokens(mod + ['model-version']) == version:
    #                 return mod[3]
    #     else:
    #         setup_logger.error("Invalid model name/version")
    #         return "Invalid model name/version"

    def getModelScoring(self):
        return self.scoring

    def getModelPath(self):
        return self.modelpath

    # To-Do
    def getModelProp(self):
        return ''

    '''
    We require the following function 
    to bridge the path that model registry UI creates and the path that the App backend expects 
    '''

    def convert_path_to_bd_fs_mnt(self, path):
# TODO modify PATH_DATA with s3 if s3:// protocol
# /project_repo/s3
        if re.findall("^s3:/", path):
            return re.sub("^s3:/", "/bd-fs-mnt/project_repo/s3", path)
        elif re.findall("^https?://", path):
            return re.sub("^https?://[a-zA-Z0-9.-]*:[0-9]*", "/bd-fs-mnt/project_repo/s3", path) 
        return re.sub("^repo:/", "/bd-fs-mnt", path)
 
#        return path.replace("repo:/", "/bd-fs-mnt")
