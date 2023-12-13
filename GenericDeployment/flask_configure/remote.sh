#!/bin/bash
#
# Copyright 2018 (c) BlueData Software, Inc.
#
#HACKY FIXME, add retries
#bdvcli --cp --node=$1 --src=$2 --dest=$3 --perms=777
bdvcli --execute --remote_node=$1 --script=$3
