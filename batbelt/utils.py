#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

"""
    The infamous utils.py module filled with functions you don't where else
    to put.
"""


import calendar


CLASSIC_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


def to_timestamp(datetime):
    """
        Return a timestamp for the given datetime object.

        Example:

            >>> import datetime
            >>> to_timestamp(datetime.datetime(2000, 1, 1, 1, 1, 1, 1))
            946688461
    """
    return calendar.timegm(datetime.timetuple())

