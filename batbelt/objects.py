#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu



from functools import wraps


__all__ = ['import_from_path', 'attr', 'dynamicmethod', 'NullObject', 'Null']


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


class Singleton(type):
    """
        Metaclass implementing the Singleton pattern.

        Usage:

            >>> class Test(object):
            ...     __metaclass__ = Singleton
            ...
            >>> id(Test()) == id(Test())
            True
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]



class NullObject(object):
    """

        Null object pattern implementation. This object is a singleton. It
        accept any parameters, and attribute lookup and any method calls,
        and always return itself.

        Example:

            >>> n = NullObject()
            >>> n
            NullObject()
            >>> n == NullObject('value') == NullObject('value', param='value')
            True
            >>> n() == n('value') == n('value', param='value') == n
            True
            >>> n.attr1
            NullObject()
            >>> n.attr1.attr2
            NullObject()
            >>> n.method1()
            NullObject()
            >>> n.method1().method2()
            NullObject()
            >>> n.method('value')
            NullObject()
            >>> n.method(param='value')
            NullObject()
            >>> n.method('value', param='value')
            NullObject()
            >>> n.attr1.method1()
            NullObject()
            >>> n.method1().attr1
            NullObject()
            >>> n.attr1 = 'value'
            >>> n.attr1.attr2 = 'value'
            >>> del n.attr1
            >>> del n.attr1.attr2.attr3
            >>> str(n) == ''
            True
            >>> n + 1 / 7 % 3
            NullObject()
            >>> n[1] == n[:4] == n
            True
            >>> 'test' in n
            False
            >>> n['test']
            NullObject()
            >>> NullObject() >> 1
            NullObject()
            >>> NullObject() == None
            True


        Iterating on NullObject() will end up in a infinite loop with the next item
        always beeing NullObject(). Stuff like sorted() will hang.
    """

    def __init__(self, *args, **kwargs):
        """
            NullObject accept any arguments
        """
        pass

    def __repr__(self):
        return "NullObject()"

    def __str__(self):
        return ""

    def __eq__(self, other):
        """
            NullObject is only equal to itself or None
        """
        return isinstance(other, NullObject) or other is None

    # Like None, NullObject is False is a boolean context
    __nonzero__ = __bool__ = lambda self: False

    # Any attribute lookup, method call or operation on NullObject returns NullObject
    nullify = lambda self, *x, **kwargs: self

    __call__ = nullify
    __getattr__ = __setattr__ = __delattr__ = nullify
    __cmp__ = __ne__ = __lt__ = __gt__ = __le__ = __ge__ = nullify
    __pos__ = __neg__ = __abs__ = __invert__ = nullify
    __add__ = __sub__ = __mul__ = __mod__ = __pow__ = nullify
    __floordiv__ = __div__ = __truediv__ = __divmod__ = nullify
    __lshift__ = __rshift__ = __and__ = __or__ = __xor__ = nullify
    __radd__ = __rsub__ = __rmul__ = __rmod__ = __rpow__ = nullify
    __rfloordiv__ = __rdiv__ = __rtruediv__ = __rdivmod__ = nullify
    __rlshift__ = __rrshift__ = __rand__ = __ror__ = __rxor__ = nullify
    __iadd__ = __isub__ = __imul__ = __imod__ = __ipow__ = nullify
    __ifloordiv__ = __idiv__ = __itruediv__ = __idivmod__ = nullify
    __ilshift__ = __irshift__ = __iand__ = __ior__ = __ixor__ = nullify
    __getitem__ = __setitem__ = __delitem__ = nullify
    __getslice__ = __setslice__ = __delslice__ = nullify
    __reversed__ = nullify
    __contains__ = __missing__ = nullify
    __enter__ = __exit__ = nullify

    # Some spacial methods cannot be transformed because they should
    # return special types:
    # __int__ = __long__ = __float__ = __complex__ = __oct__ = __hex__ = ...
    # __index__ = __trunc__ = __coerce_ = ...
    # __len__ = ...
    # __iter__ = ...
    #  __round__ = __floor__ = __ceil__ = __trunc__ = ...


# One official instance off NullObject, that can be used like None
Null = type('Null', (NullObject,), {"__repr__": lambda s: "Null"})()
