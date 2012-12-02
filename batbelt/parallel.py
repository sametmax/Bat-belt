#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu





import threading
import multiprocessing
from functools import wraps
from Queue import Empty

__all__ = ['process', 'thread']


def process(*proxy_args, **proxy_kwargs):

    fire = proxy_kwargs.pop('fire', False) or proxy_args or proxy_kwargs

    def decorator(func):

        if fire:

            @wraps(func)
            def fun(*args, **kwargs):
                func(*args, **kwargs)

            fun.process = multiprocessing.Process(target=fun, args=proxy_args,
                                                   kwargs=proxy_kwargs)
            fun.process.start()

            return fun

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                process = multiprocessing.Process(target=func, args=args,
                                                  kwargs=kwargs)
                process.start()
                return process

            return wrapper

    return decorator


def thread(*proxy_args, **proxy_kwargs):

    fire = proxy_kwargs.pop('fire', False) or proxy_args or proxy_kwargs

    def decorator(func):

        if fire:

            @wraps(func)
            def fun(*args, **kwargs):
                func(*args, **kwargs)

            fun.thread = threading.Thread(target=fun, args=proxy_args,
                                           kwargs=proxy_kwargs)
            fun.thread.start()

            return fun

        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                thread = threading.Thread(target=func, args=args,
                                          kwargs=kwargs)
                thread.start()
                return thread

            return wrapper

    return decorator


class StopWorker():
    pass


def worker(block=True, timeout=0.1, method='process'):
    """
        Turn a function into a worker:

            from parallel import worker

            @worker()
            def test(mot):
                print "in %s" % mot
                return mot

            process = test.start()

            for x in range(10):
                process.put(x)

            for x in range(10):
                print "out %s" % process.get()

            process.stop()

        Which outputs:

            in 0
            out 0
            in 1
            in 2
            out 1
            in 3
            out 2
            in 4
            out 3
            out 4
            in 5
            out 5
            in 6
            out 6
            in 7
            out 7
            in 8
            out 8
            in 9
            out 9

        If an exception occures, it will be send back in the message queue.

        So you may want to check the result with isintance().
    """

    def decorator(func):

        if method == 'thread':
            Queue = threading.Queue
            Manager = threading.Thread
            Error = threading.TimeoutError
        else:
            Queue = multiprocessing.Queue
            Manager = multiprocessing.Process
            Error = multiprocessing.TimeoutError

            in_queue = Queue()
            out_queue = Queue()

            def main_loop():

                while True:
                    try:

                        res = in_queue.get(block, timeout)

                        if isinstance(res, StopWorker):
                            break

                        out_queue.put(func(res))

                    except (Error, Empty):
                        pass
                    except (StopWorker, KeyboardInterrupt):
                        break
                    except Exception as e:
                        out_queue.put(e)

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            def get(block=block, timeout=timeout):
                res = out_queue.get(block, timeout)
                if isinstance(res, Exception):
                    raise res
                return res

            wrapper.manager = Manager(target=main_loop)
            wrapper.manager.get = get
            wrapper.manager.stop = lambda: in_queue.put(StopWorker(), block, timeout)
            wrapper.manager.put = lambda x: in_queue.put(x, block, timeout)
            wrapper.TimeoutError = Error
            wrapper.start = lambda: wrapper.manager.start() or wrapper.manager

            return wrapper

    return decorator
