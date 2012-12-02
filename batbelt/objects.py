#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu



from functools import wraps


__all__ = ['import_from_path', 'attr', 'dynamicmethod']


def import_from_path(path):
    """
        Import a class dynamically, given it's dotted path.
    """
    module_name, class_name = path.rsplit('.', 1)
    try:
        return getattr(__import__(module_name, fromlist=[class_name]), class_name)
    except AttributeError:
        raise ImportError('Unable to import %s' % path)



def attr(obj, *attrs, **kwargs):
    """
        Follow chained attributes and get the value of the last attributes.
        If an attribute error is raised, returns the default value.

        res = attr(data, 'test', 'o', 'bla', default="yeah")

        is the equivalent of

        try:
            res = getattr(getattr(getattr(data, 'test'), 'o'), 'bla')
        except AttributeError:
            res = "yeah"

    """
    try:
        value = getattr(obj, attrs[0])

        for attr in attrs[1:]:
            value = getattr(value, attr)
    except (IndexError, AttributeError):
        return kwargs.get('default', None)

    return value


class InstanceAndClassMethodDescriptor(object):
    """
        Return a wrapper around the method calling the method as a classmethod
        or as a normal method depending of if it's called from an instance
        or a class.
    """

    def __init__(self, method):
        self.method = method

    def __get__(self, obj, obj_type):

        @wraps(self.method)
        def wrapper(*args, **kwargs):
            return self.method(obj or obj_type, *args, **kwargs)

        return wrapper



def dynamicmethod(func):
    """
        Wrap the method so it becomes a function wich will receives the first
        parameter as been the class or the instance depanding of if it's called
        from a class or an instance.
    """
    return InstanceAndClassMethodDescriptor(func)


