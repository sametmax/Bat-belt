#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

"""
    The infamous utils.py module filled with functions you don't where else
    to put.
"""


import sys
import calendar


CLASSIC_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
CLASSIC_DATETIME_PATTERN = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'




def to_timestamp(datetime):
    """
        Return a timestamp for the given datetime object.

        Example:

            >>> import datetime
            >>> to_timestamp(datetime.datetime(2000, 1, 1, 1, 1, 1, 1))
            946688461
    """
    return calendar.timegm(datetime.timetuple())


class ImportableItems(list):

    def __init__(self, *args, **kwargs):
        super(ImportableItems, self).__init__(*args, **kwargs)
        self.non_importable_items = {}

    def append(self, item_name):
        self.non_importable_items.pop(item_name, None)
        super(ImportableItems, self).append(item_name)


def import_list(*args):
    """
        Allow to create easily a __all__ listing for a module.

        Returns a value for __all__ and a decorator to add anything
        to it easily.
    """

    importable_items = ImportableItems()
    importable_items.non_importable_items.update(sys._getframe(1).f_globals)
    for item in args:
        importable_items.append(item)


    def importable(func, name=None):

        if name is None:
            try:
                name = func.__name__
            except AttributeError:
                raise ValueError('You must provide a name for '
                                 'this item: %s' % repr(func))
        importable_items.append(name)

        return func

    return importable_items, importable

