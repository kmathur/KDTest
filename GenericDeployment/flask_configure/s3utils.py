import os, json, base64, sys, logging, re
import hashlib
import getpass
import boto3
from botocore.client import Config

#TODO use configmeta
#from configcli3 import ConfigCli
#configcli = ConfigCli(shell=False)
#ConfigMeta = configcli.getCommandObject("namespace")

#TODO use multiple secrets for different s3 backend types (kubedirector label kubedirector.hpe.com/s3backendType: <minio> or <aws>)

#TODO this might change in the future release
secretType = 'mlflow-s3-credentials' 


def base64d(value, decode_format='utf-8'):
    '''base64 decode'''
    if not value: return # return null for optional secrets
    return base64.b64decode(value).decode(decode_format)

        
 
class s3_util( object ):
    def __init__(self):
        self.info = {}
        try:
#TODO: use configmeta
            #self.get_secret_from_ConfigMeta(secretType)
            self.get_secret_from_json(secretType)
        except:
            print("failed to fetch tenant info")
            sys.exit(0)

    def get_configmaps_from_ConfigMeta(self):
#TODO: use configmeta
        #configmap = ConfigMeta.getWithTokens(["connections", "configmaps", "model"])
        #models = ConfigMeta.getWithTokens(["connections", "configmaps", "model"])
        #for k in models:
        #    self.info[k] = ConfigMeta.getWithTokens(["connections", "configmaps", "model", "data", k])
        #secrets = ConfigMeta.getWithTokens(["connections", "secrets", secretType, "data"])
        #for k in secrets:
        #    self.info[k] = base64d(ConfigMeta.getWithTokens(["connections", "secrets", secretType, "data", k]))
        pass

    def get_secrets_from_ConfigMeta(self, secretType):
#TODO: use configmeta
        pass

    def get_configmaps_from_json(self):
        try: 
            with open('/etc/guestconfig/configmeta.json','r') as f:
                config = json.load(f) 
            models = config['connections']['configmaps']['model']
            return models if type(models)==list else [models] # return a list for any number of models
        except:
            print("failed to fetch configmaps")
            sys.exit(0)

    def get_secret_from_json(self, secretType):
        try:
            with open('/etc/guestconfig/configmeta.json','r') as f:
                config = json.load(f) 
            secrets = config['connections']['secrets'][secretType][0]['data']
            for k, v in secrets.items():
                self.info[k] = base64d(v)
        except:
            print("failed to fetch secrets")
            sys.exit(0)

    def get_source_dest(self, url, repo):
        '''
        example:
          url = repo://local/repo/model3.pkl
          url = s3://hpe/data/model3.pkl
          url = http://<hpe-pulic-ip>:<port>/mlflow/data/scoring.pkl 
        '''
        if re.findall('^repo://',url):
            return (None, None, None)  # skip download
        elif re.findall('^(s3|http|https)://', url): # if remote s3 found
            if re.findall('^s3://',url):
                tmp = re.sub('s3://','', url) # remove s3:// or any url protocal
            else:
                self.info['ENDPOINT_URL'] = re.findall('http?://[a-zA-Z0-9.:-]*/', url)[0][:-1] # remove the end '/'
                tmp = re.sub('http?://[a-zA-Z0-9.:-]*/', '', url)
            tmp = tmp.strip('/').rstrip().lstrip().split('/') # remove leading '/', and split path into a list
            bucket = tmp[0]
            dirs = tmp[1:] 
            source_path = '/'.join(dirs)  
            dest_folder = os.path.join(repo, "s3", bucket, *dirs[:-1]) 
            os.makedirs(dest_folder, exist_ok=True) # local file path
            dest_path = os.path.join(repo, "s3", bucket, *dirs)
            return bucket, source_path, dest_path
        else: # local path found, don't download 
            return (None, None, None)

         
    def download(self, repo='/bd-fs-mnt/project_repo/', **kwargs):
        '''Download from s3 to local repo'''
        # pass all s3-download data into info
        # download remote (AWS, s3, or don't download) to local project_repo bucket
        # donwload model, scoring script
        try:
            self.info['MODEL_BUCKET'], self.info['MODEL_SOURCE'], self.info['MODEL_DEST'] = self.get_source_dest(self.info.get('MODEL'), repo)
            self.info['SCORING_BUCKET'], self.info['SCORING_SOURCE'], self.info['SCORING_DEST'] = self.get_source_dest(self.info.get('SCORING_SCRIPT'), repo)
            # create local project_repo bucket
            try:
                kwargs['aws_access_key_id'] = self.info.get('S3_ACCESS_KEY_ID')
                kwargs['aws_secret_access_key'] = self.info.get('S3_SECRET_ACCESS_KEY')
                kwargs['config'] = Config(signature_version='s3v4')            
                kwargs['endpoint_url'] = self.info.get('ENDPOINT_URL')
                print("Make sure don't set proxy in yaml if endpoint_url is used")
                # S3 Connect
                s3 = boto3.resource('s3', **kwargs)
                try:
                    if self.info.get('MODEL_DEST'):
                        s3.Bucket(self.info['MODEL_BUCKET']).download_file(self.info['MODEL_SOURCE'], self.info['MODEL_DEST'])
                        print("Model downloaded from S3")
                    else:
                        print("No model downloaded from S3, using local model")
                    if self.info.get('SCORING_DEST'):
                        s3.Bucket(self.info['SCORING_BUCKET']).download_file(self.info['SCORING_SOURCE'],self.info['SCORING_DEST'])
                        print("Scoring script downloaded from S3")
                    else:
                        print("No scoring script downloaded from S3, using local scoring script")
                except:
                    print('You might need to provide the correct aws_access_key_id and aws_secret_access_key or correct model and scoring script name .')
                    raise
            except:
                raise
        except:
            raise

    def main(self, **kwargs):
        try:
            models = self.get_configmaps_from_json()
            for model in models:
                self.info["MODEL"] = model['data']['path'] # multiple models (e.g., a remote & a local model)
                self.info["SCORING_SCRIPT"] = model['data']['scoring-path']
                self.download() 
        except:
            print('Failed to download')
            sys.exit(0)

if __name__ == '__main__':
    '''
    # check if secrets have all the requirements 
       
      - s3 key ID
      - s3 secret access key
      - source s3://hpe/data/model.pkl
      - endpoint_url  
     
    # donwload the model to project repo
    # create path with bucket and dest
    /bd-fs-mnt/project_repo/s3/hpe/data
    '''
    try:
       s3_util().main()
    except Exception as e:
       sys.exit(0)
 
