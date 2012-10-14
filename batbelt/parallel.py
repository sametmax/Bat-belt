#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu


from functools import wraps
from multiprocessing import Process
from threading import Thread


__all__ = ['process', 'thread']


def process(*proxy_args, **proxy_kwargs):

    fire = proxy_kwargs.pop('fire', False) or proxy_args or proxy_kwargs

    def decorator(func):

        if fire:

            @wraps(func)
            def fun(*args, **kwargs):
                func(*args, **kwargs)

            fun.process = Process(target=fun, args=proxy_args,
                                      kwargs=proxy_kwargs)
            fun.process.start()

            return fun

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                wrapper.process = Process(target=func, args=args,
                                          kwargs=kwargs)
                wrapper.process.start()
                return wrapper.process

            return wrapper

    return decorator


def thread(*proxy_args, **proxy_kwargs):

    fire = proxy_kwargs.pop('fire', False) or proxy_args or proxy_kwargs

    def decorator(func):

        if fire:

            @wraps(func)
            def fun(*args, **kwargs):
                func(*args, **kwargs)

            fun.thread = Thread(target=fun, args=proxy_args,
                                      kwargs=proxy_kwargs)
            fun.join = lambda: fun.thread.join()
            fun.thread.start()

            return fun

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                wrapper.thread = Thread(target=func, args=args,
                                          kwargs=kwargs).start()
                return wrapper.thread

            wrapper.join = lambda: wrapper.thread.join()

            return wrapper

    return decorator
