#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

"""
    The infamous utils.py module filled with functions you don't where else
    to put.
"""


import sys
import os

from datetime import datetime


CLASSIC_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
CLASSIC_DATETIME_PATTERN = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}'




def to_timestamp(dt):
    """
        Return a timestamp for the given datetime object.

        Example:

            >>> import datetime
            >>> to_timestamp(datetime.datetime(2000, 1, 1, 1, 1, 1, 1))
            946688461
    """
    return (dt - datetime(1970, 1, 1)).total_seconds()


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



def add_to_pythonpath(path, starting_point='.', insertion_index=None):
    """
        Add the directory to the sys.path.

        You can path an absolute or a relative path to it.

        If you choose to use a relative path, it will be relative to
        `starting_point` by default, which is set to '.'.

        You may want to set it to something like __file__ (the basename will
        be stripped, and the current file's parent directory will be used
        as a starting point, which is probably what you expect in the
        first place).

        :example:

        >>> add_to_pythonpath('../..', __file__)
    """

    if not os.path.isabs(path):

        if os.path.isfile(starting_point):
            starting_point = os.path.dirname(starting_point)

        path = os.path.join(starting_point, path)

    path = os.path.realpath(os.path.expandvars(os.path.expanduser(path)))

    if path not in sys.path:
        if insertion_index is None:
            sys.path.append(path)
        else:
            sys.path.insert(insertion_index, path)

