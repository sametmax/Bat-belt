#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu


import sys

from functools import wraps

from io import BytesIO
from contextlib import contextmanager


@contextmanager
def capture_ouput(stdout_to=None, stderr_to=None):
    """
        Context manager that captures any printed ouput in the 'with' block.

        :Example:

        >>> with capture_ouput() as (stdout, stderr):
        ...    print "hello",
        ...
        >>> print stdout.getvalue().upper()
        HELLO
        >>> with capture_ouput() as (stdout, stderr):  # doctest: +IGNORE_EXCEPTION_DETAIL
        ...    assert False
        ...
        Traceback (most recent call last):
        AssertionError
        >>> from tempfile import NamedTemporaryFile
        >>> f = NamedTemporaryFile(mode="rw+b")
        >>> with capture_ouput(f) as (stdout, stderr):
        ...    print "hello",
        ...
        >>> print stdout.read()
        hello


        .. :warning: this is NOT thread safe.

        .. :note: The file like objects containing the capture are not closed
                  automatically by this context manager. You are responsible
                  to do it.

    It does not capture exception, so they bubble out and print the stack
    trace anyway.
    """

    try:

        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = c1 = stdout_to or BytesIO()
        sys.stderr = c2 = stderr_to or BytesIO()
        yield c1, c2

    finally:

        sys.stdout = stdout
        sys.stderr = stderr

        try:
            c1.flush()
            c1.seek(0)
        except (ValueError, TypeError):
            pass

        try:
            c2.flush()
            c2.seek(0)
        except (ValueError, TypeError):
            pass


def decorator_with_args(wrap=True,
                        function_assigned=('__module__', '__name__', '__doc__'),
                        function_updated=('__dict__',),
                        decorator_assigned=('__module__', '__name__', '__doc__'),
                        decorator_updated=('__dict__',),
                        ):
    """
        Use this decorator on a wannabe decorator.

        It will turn it into a decorator that accept any arguments and
        wraps the resulting decorated function unless you set wrap=False.

        Usage:

            # You use @decorator_with_args on a function you wish to
            # be a decorator accepting arguments
            @decorator_with_args()
            def your_decorator(func, *args, **kwargs):
                def wrapper():
                    # do stuff
                    return func()
                return wrapper

        Your decorator must accept the function as the first argument, and
        expact the other arguments after that. It doesn't have to be *args,
        **kwargs, it can be any signature, as long as the first argument,
        is the function to decorate.

        One your wannabe decorator decorated, you can use it this way:

            # When you use YOUR decorator, you will be able to pass arguments
            @your_decorator(arg1, arg2, arg3='foo')
            def a_function():
                # do stuff

            # If you don't use arguments, you still need the parenthesis
            @your_decorator()
            def another_function():
                # do stuff

        By default, @decorator_with_args will attempt to apply functools.wraps on
        the wrapper your wannabe decorator returns. If you don't wish that,
        pass wrap=False:

            @decorator_with_args(wrap=False)
            def your_decorator(func, *args, **kwargs):
                def wrapper():
                    # do stuff
                    return func()
                # This will be passed to functools.wraps() if you don't
                # set wrap=False
                return wrapper

        You can also pass the same arguments you would pass to functools.wraps
        directly to @decorator_with_args. They will be passed to along:

            @decorator_with_args(function_assigned=('__module__', '__name__', '__doc__'))
            def your_decorator(func, *args, **kwargs):
                def wrapper():
                    # do stuff
                    return func()
                # this will apply functools.wrap() with assigned being set to
                # ('__module__', '__name__')
                return wrapper

        The params are named function_assigned and function_updated instead of
        just assigned and updated like in functools.wraps.

        Also, @decorator_with_args will ALWAYS apply functools.wraps to the
        wrapper around your wannabe decorator. You can also control what's
        copied by passing decorator_assigned and decorator_updated the same way:

            # functools.wrap will always be applied to your_decorator()
            # but you can choose with which arguments
            @decorator_with_args(decorator_updated=('__dict__',))
            def your_decorator(func, *args, **kwargs):
                def wrapper():
                    # do stuff
                    return func()
                return wrapper

    """
    # decorator() will return this function, wich will be the real decorator
    # called on the wannabe decorator.
    def _decorator(wannabe_decorator):

        # This is the function that will return your wrapped wannabe decorator.
        # Il will add a wrapper that will call your wannabe decorator with
        # the arguments stored in a closure under the hood.
        def decorator_maker(*args, **kwargs):

            # This is the the wrapper around your wannabe decorator. It
            # replaces your function so it can pass arguments to it.
            # We apply @wraps on it so it takes all metadata from
            # the wannabe decorator and attach them to itself.
            @wraps(wannabe_decorator, decorator_assigned, decorator_updated)
            def decorator_wrapper(func):

                # The wrapper calls your wannabe decorator, passing the
                # function to decorate and arguments to it.
                # It will get the wrapper your wannabe decorator returns,
                # and if, wrap=True (default), will apply @wraps on it too.
                d = wannabe_decorator(func, *args, **kwargs)
                if wraps:
                    d = wraps(func, function_assigned, function_updated)(d)
                return d

            return decorator_wrapper

        return decorator_maker

    return _decorator


class MultiStopIteration(StopIteration):
    def throw(self):
        raise self



@contextmanager
def multibreak():
    '''

        Context manager which allow to break multiple nested for loops at once.

        Example:

            >>> with multibreak() as stop:
            ...     for x in range(1, 4):
            ...         for z in range(1, 4):
            ...             for w in range(1, 4):
            ...                 print w
            ...                 if x * z * w == 2 * 2 * 2:
            ...                     print 'stop'
            ...                     stop()
            ...
            1
            2
            3
            1
            2
            3
            1
            2
            3
            1
            2
            3
            1
            2
            stop
    '''

    try:
        yield MultiStopIteration().throw
    except MultiStopIteration:
        pass


def accept_callbacks(func):
    """
       A decorator to allow any function to be able to accept callbacks.

       :Example:

            # make your function accept callbacks
            @accept_callbacks
            def add(a, b):
                return a + b

            # write a callback that accept 'result' as the first parameter
            # and the function paramters as other parameters
            def my_callback(result, a, b):
                print("Function called with a=%s et b=%s !" % (a, b))
                print("It returned '%s'" % result)

            # add the callback to the callback list
            add.callbacks.append(my_callback)

            # enjoy
            >>> add(1, 2)
            Function called with a=1 et b=2 !
            It returned '3'
            3

    """

    callbacks = []

    @wraps(func)
    def wrapper(*args, **kwargs):

        result = func(*args, **kwargs)

        for callback in callbacks:
            callback(result, *args, **kwargs)

        return result

    wrapper.callbacks = callbacks

    return wrapper
