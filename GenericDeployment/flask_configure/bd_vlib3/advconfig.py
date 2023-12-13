#!/bin/env python
#
# Copyright (c) 2015 BlueData Software, Inc.

import json
from .errors import *
from .utils import *

BDVLIB_ADVCFG_RESTART_ALL_SRVCS="all"

class BDVLIB_AdvancedConfig(object):
    """
    Parses the read-only advanced configurations stored in a file and provides
    a key-value based lookup.
    """

    def __init__(self):
        """
        """
        return

    def listNamespaces(self):
        """
        DEPRECATED: Lists the available namsepaces whose configurations are
                    specified.
        """
        return []

    def getProperties(self, Namespace):
        """
        DEPRECATED: Returns a list of 'key=value' pairs defined in the requested
                    namespace.
        """
        return []

    def restartService(self, Services=BDVLIB_ADVCFG_RESTART_ALL_SRVCS):
        """

        """
        Srvcs=''
        if isinstance(Services, list):
            Srvcs = ','.join(Services)
        elif isinstance(Services, str):
            Srvcs = Services
        else:
            raise Exception("Unknown input type: %s" % (type(Services)))

        return restart_services(Srvcs)
