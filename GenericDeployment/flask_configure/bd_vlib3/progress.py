#!/bin/env python
#
# Copyright (c) 2015 BlueData Software, Inc.

from .errors import DescTooLongException, PercentageOutOfRangeException
from .utils import notify_progress

MAX_DESC_STR_LEN=64

def BDVLIB_Progress(percentage, description):
    """
    Reports progress of the configuration. This information is propagated all
    the way to the user's interface.

    Parameters:
        percentage: is a number between 0 and 100 (both inclusive)
        description: a short descriptive string less than 64chars.

    Returns:
        0 on success.
        1 on any failure.
    Exceptions:
        DescTooLongException: The description string provided is too long.
        PercentageOutOfRangeException:
    """
    if len(description) > MAX_DESC_STR_LEN:
        raise DescTooLongException()

    if (int(percentage) > 100) or (int(percentage) < 0):
        raise PercentageOutOfRangeException()

    return notify_progress(percentage, description)
