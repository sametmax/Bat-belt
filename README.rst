*************************************************************
A collection of gagdets that makes Python even more powerful
*************************************************************

There is not real structure for this lib, it's just a bunch of snippets I put together because I use them often.

Not all of them are documented here, few of them have tests, it's zlib licence, you know the drill...


To timestamp
=============

<code>datetime.fromtimestamp</code> exists but not the other away around, and it's not likely to change anytime soon (see: http://bugs.python.org/issue2736). In the meantime::

    >>> from datetime import datetime
    >>> to_timestamp(datetime(2000, 1, 1, 2, 1, 1))
    946692061
    >>> datetime.fromtimestamp(946688461) # tu as codé celle là et pas l'autre connard !
    datetime.datetime(2000, 1, 1, 2, 1, 1)


Get this nest value or a default
=================================

Don't::

    try:
        res = data['key'][0]['other key'][1]
    except (KeyError, IndexError):
        res = "value"


Do::

    get(data, 'key', 0, 'other key, 1, default="value")


For attributes::

    devise = attr(car, 'insurance', 'expiration_date', 'timezone')


Iteration tools missing in itertools
===================================================================================


Iteration by chunk or with a sliding window::

    >>> for chunk in chunks(l, 3):
    ...     print list(chunk)
    ...
    [0, 1, 2]
    [3, 4, 5]
    [6, 7, 8]
    [9]
    >>> for slide in window(l, 3):
    ...     print list(slide)
    ...
    [0, 1, 2]
    [1, 2, 3]
    [2, 3, 4]
    [3, 4, 5]
    [4, 5, 6]
    [5, 6, 7]
    [6, 7, 8]
    [7, 8, 9]


Get the first element an any iterable (not just indexable) or the first one to be True::

    >>> first(xrange(10))
    0
    >>> first_true(xrange(10))
    1
    >>> first([], default="What the one thing we say to the God of Death ?")
    'What the one thing we say to the God of Death ?'

Sorted Set
===================================================================================

Slow but useful data structure::

    >>> for x in sset((3, 2, 2, 2, 1, 2)):
    ...     print x
    ...
    3
    2
    1


Dictionaries one liners
===================================================================================


I wish <code>+</code> was overloaded for dicts::

    >>> dmerge({"a": 1, "b": 2}, {"b": 2, "c": 3})
    {'a': 1, 'c': 3, 'b': 2}


Sometimes you do not want to simply overwrite the values inside the original dict, but merge them in custom fashion::

    >>> def my_merge(v1, v2):
    ...     if isinstance(v1, dict) and isinstance(v2, dict):
    ...         return dmerge(v1, v2)
    ...     return v2
    >>> dmerge({"a": 1, "b": {'ok': 5}}, {"b": {'ko': 5 }, "c": 3}, my_merge)
    {'a': 1, 'c': 3, 'b': {'ko': 5, 'ok': 5}}

Original dicts are not modified, but this will modify them::

    >>> from batbelt.structs import rename
    >>> rename({"a": 1, "b": 2})
    >>> rename({"a": 1, "b": 2}, 'b', 'z')
    {u'a': 1, u'z': 2}

(not thread safe).

Twited but satisfying::

    >>> from batbelt.structs import unpack
    >>> dct = {'a': 2, 'b': 4, 'z': 42}
    >>> a, b, c = unpack(dct, 'a', 'b', 'c', default=1)
    >>> a
    2
    >>> b
    4
    >>> c
    1


String tools
===================================================================================

The mandatory "slufigy"::

    >>> slugify(u"Hélo Whorde")
    helo-whorde

You get better slugification if you install the `unidecode` lib, but it's optional. You can specify `separator` if you don't like `-` or call directly `normalize()` (the underlying function) if you wish more control.

The module also feature html_escape/unescape that is not useless and json_dumps/loads that understand datetime by default. Look at the source for these, I'm lazy (PL for documentation are welcome).

There is also a poor man template system using the `format()` string method on a file content. No loop, but still nice for quick and dirty file generation :

    from batbelt.strings import render

    render('stuff.conf.tpl', {"var": "value"}, "/etc/stuff.conf")


Import this
===================================================================================


`__import__` is weird. Let's abstract that ::

    TaClasse = import_from_path('foo.bar.TaClasse')
    ton_obj = TaClasse()


Catpure prints
===================================================================================


A context manager to deal with this libs that print the result instead of returning it :


    >>> with capture_ouput() as (stdout, stderr):
    ...    print "hello",
    ...
    >>> print stdout.read()
    hello
    >>> stdout.close()


Create a decorator that accept arguments
===================================================================================


I never remember how to do this. And I don't have to anymore.

First, write the decorator::

    # all arguments after 'func' are your decorator argument
    @decorator_with_args()
    def your_decorator(func, arg1, arg2=None):

        if arg1:
            # do stuff here

        # do your usual decorator jimbo jumbo, wrapping, calling, returning...
        def wrapper():
            return func(arg2)


        return wrapper



Enjoy :

    @your_decorator(False, 1)
    def hop(un_arg):
        # do stuff in the decorated function


Poor man task queue
===================================================================================================


You don't always need the guaranty of a big lib, you just need a little worker to do the job outside of the main thread::



    from batbelt.parallel import worker

    @worker()
    def task(arg):
        arg = arg + 10
        return arg


    # start the worker
    process = task.start()

    # send tasks
    for x in range(10):
        process.put(x)

    # (optionaly) get results
    for x in range(10):
        print process.get()

    ## 10
    ## 11
    ## 12
    ## 13
    ## 14
    ## 15
    ## 16
    ## 17
    ## 18
    ## 19

    # stop the worker
    process.stop()

Le worker use subprocess by default, but if you prefer threads: `@worker(method="tread")`.

If you look for it in the source code, you'll see goodies such as Singletong, Null Pattern implementation and other things you don't use that often.
