import os
from typing import List
from pathlib import Path
from configcli3 import ConfigCli
LOADBALANCER = "LoadBalancer"

class ConfigCliOps:
    
    def __init__(self, *args, **kwargs):
        configcli=ConfigCli(shell=False)
        self.ConfigMeta=configcli.getCommandObject("namespace")

    def get_with_tokens(self, jsonpath: List[str]) -> str:
        return self.ConfigMeta.getWithTokens(jsonpath)

configcliops = ConfigCliOps()

def get_nodegroups() -> List[int]:
    """
    Returns all the nodegroups as a list of ints
    :return: List of nodegroups as an int
    """

    nodegroups = os.popen("bdvcli -g nodegroups").read().rstrip()
    print(type(nodegroups))
    return [int(x) for x in nodegroups.split(",")]


def get_roles(nodegroup: int) -> List[str]:
    """
    Returns all the roles associated with the nodegroup
    :param nodegroup: int
    :return: list of all the roles
    """
    roles = os.popen("bdvcli -g nodegroups.{}.roles".format(nodegroup)).read().rstrip()
    return list(roles.split(","))


def is_loadbalancer(nodegroup: int) -> bool:
    """
    Returns true if the nodegroup has a role named LOADBALANCER
    :param nodegroup: nodegroup number
    :return: bool indicating if the nodegroup has a LoadBalancer
    """
    return True if LOADBALANCER in get_roles(nodegroup) else False


def k8s_is_loadbalancer():
    role_id = os.popen("bdvcli -g node.role_id").read().rstrip()
    return True if role_id is "LoadBalancer" else False

def get_loadbalancer_fqdn() -> str:
    """
    Returns the FQDN for loadBalancer
    :return: FQDN as a string
    """
    #for nodegroup in get_nodegroups():
    #    if is_loadbalancer(nodegroup):
    #        return os.popen("bdvcli -g nodegroups.{}.roles.LoadBalancer.fqdns".format(nodegroup)).read().rstrip()

    # Temporary change for KubeDirector
    '''LBFile = my_file = Path("/usr/lib/mysql_files/ConfigMeta")
    if LBFile.is_file():
        with open(LBFile, "r") as f:
            fqdn = eval(f.read())["fqdn"]
        return str(fqdn)
    '''

    return configcliops.get_with_tokens(["nodegroups", "1", "roles", "LoadBalancer", "fqdns"])[0]

def get_external_endpoints() -> str:
    """
    Returns the external endpoint for LoadBalancer
    :return: endpoint URL as a string
    """
    # Temporary change for k8s
    # LBFile = my_file = Path("/usr/lib/mysql_files/ConfigMeta")
    # if LBFile.is_file():
    #     with open(LBFile, "r") as f:
    #         endpoint = eval(f.read())["external_endpoint"]
    #     return str(endpoint)

    return configcliops.get_with_tokens(["nodegroups", "1", "roles", "LoadBalancer", "services","gunicorn","endpoints"])[0]
