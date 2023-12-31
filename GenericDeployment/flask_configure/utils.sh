#!/bin/env bash
################################################################################
# Copyright (c) 2015, BlueData Software, Inc.                                  #
#                                                                              #
# Common/Utility functions for guest configuration (bash shell) scripts.       #
#                                                                              #
# Requirements:                                                                #
#    - logging.sh must be sourced before sourcing this file.                   #
#
################################################################################

# Uncomment this block if you want xtrace enabled.
#############
#exec {XTRACE_FD}>>/tmp/test.xtrace
#PS4='${BASH_SOURCE##*/} ${LINENO}: '
#BASH_XTRACEFD=${XTRACE_FD}
#set -x
#############

# A convienence function to invoke BD_VLCI and fail if the return status is
# non-zero. In almost all cases, a failure in invoking BD_VCLI is a fatal error
# and the Guest configuration Script cannot make forwand progress any way.
invoke_bdvcli() {
    invoke_bdvcli_ignore_error $@

    STATUS=$?
    if [[ ${STATUS} -ne 0 ]]; then
        log_error "Failed (status: ${STATUS}) to execute: /usr/bin/bd_vcli ${@}"
        exit 111
    fi
}

# A convienence function to invoke BD_VLCI but not bail out if the command
# failed. This is useful in rare cases where this failure is not fatal.
#
# CAUTION: You should really check the return status when using this.
invoke_bdvcli_ignore_error() {
    eval "/usr/bin/bd_vcli ${@}"
}

# Returns the current time of this invocation in YYYYmmddHHMMSS format
util_timestamp() {
    date +%Y%m%d%H%M%S || true
}

# Utility function that returns success when invoked from with in a container.
# Otherwise, return a failure (non-zero return status)
util_is_container() {
    if [ -f "/proc/self/cgroup" ]; then
        cat /proc/self/cgroup | grep -q "docker"
        return $?
    else
        return 1
    fi
}

# Utility to figure out the docker ID from inside the container
util_get_docker_id() {
    if util_is_container; then
        DOCKER_ID=`cat /proc/self/cgroup | head -1 | awk -F/ '{print $3}'`
        echo $DOCKER_ID
        return 0
    else
        echo "Not a docker container"
        return 1
    fi
}

# Utility function to get the cpu share of the current container
util_get_cpu() {
    if DOCKER_ID=$(util_get_docker_id); then
        CPU=`cat /cgroup/cpu/docker/${DOCKER_ID}/cpu.shares`
        echo `expr $CPU / 1024`
        return 0
    else
        echo $DOCKER_ID
        return 1
    fi
}

# Utility function to get the memory share in gigabytes
# of the current container
util_get_memory() {
    if DOCKER_ID=$(util_get_docker_id); then
        MEMORY=`cat /cgroup/memory/docker/${DOCKER_ID}/memory.limit_in_bytes`
        echo `expr $MEMORY / 1024 / 1024 / 1024`
        return 0
    else
        echo $DOCKER_ID
        return 1
    fi
}
