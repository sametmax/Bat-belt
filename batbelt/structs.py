#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu


from collections import MutableSet, deque

from itertools import islice, chain


__all__ = ['chunks', 'dmerge', 'get', 'window', 'dswap', 'subdict', 'first',
           'first_true', 'sset']


def chunks(seq, chunksize, process=tuple):
    """
        Yields items from an iterator in iterable chunks.
    """
    it = iter(seq)
    while True:
        yield process(chain([it.next()], islice(it, chunksize - 1)))



def window(iterable, size=2):
    """
        Yields iterms by bunch of a given size, but rolling only one item
        in and out at a time when iterating.
    """
    iterable = iter(iterable)
    d = deque(islice(iterable, size), size)
    yield d
    for x in iterable:
        d.append(x)
        yield d


def dmerge(d1, d2, merge_func=None):
    """
        Create a new dictionary being the merge of the two passed as a
        parameter. If a key is in both dictionaries, the values are processed
        with the merge_func.

        By default the value in the second dictionary erases the value in the
        first one.
    """
    d = {}

    d.update(d1)

    if merge_func is None:
        d.update(d2)
        return d

    for k, v in d2.iteritems():
        if k in d:
            d[k] = merge_func(d[k], v)
        else:
            d[k] = v
    return d


def dswap(dct):
    """
        Swap key and values of a given dictionary. Return a new dictionary.

        If you have duplicate values, the last one in the dictionary order
        will be used. Since dictionary order is not predictable, you should
        make sure to either remove duplicates values before processing, or
        just make sure loosing some keys is not a problem for you.


        example:

            >>> sorted(dswap({'a': 1, 'b': 2}).items())
            [(1, 'a'), (2, 'b')]
    """
    return dict((value, key) for key, value in dct.iteritems())


def get(data, *keys, **kwargs):
    """
        Extract a data from nested mapping and sequences using a list of keys
        and indices to apply successively. If a key error or an index error
        is raised, returns the default value.

        res = get(data, 'test', 0, 'bla', default="yeah")

        is the equivalent of

        try:
            res = data['test'][0]['bla']
        except (KeyError, IndexError):
            res = "yeah"

    """
    try:
        value = data[keys[0]]

        for key in keys[1:]:
            value = value[key]
    except (KeyError, IndexError, TypeError):
        return kwargs.get('default', None)

    return value


def iget(data, value, default=None):
    """
        Same as indexing, but works with any iterable,
        and accept a default value.

        :Example:

        >>> iget(xrange(10), 0)
        0
        >>> iget(xrange(10), 5)
        5
        >>> iget(xrange(10), 10000, default='wololo')
        u'wololo'
    """

    for x in islice(data, value, None):
        return x
    return default



def rename(dct, old_name, new_name):
    """
        Rename a key in a dictionary. No effect if the key does not exists.

        Return the dictiony passed as parameter.
    """

    try:
        dct[new_name] = dct[old_name]
        del dct[old_name]
    except KeyError:
        pass

    return dct


def unpack(indexable, *args, **kwargs):
    """
        Return an generator with the values for the given keys/indices or
        a default value.

        :Example:

        >>> dct = {'a': 2, 'b': 4, 'z': 42}
        >>> a, b, c = unpack(dct, 'a', 'b', 'c', default=1)
        >>> a
        2
        >>> b
        4
        >>> c
        1
        >>> list(unpack(range(5, 10), 2, 4))
        [7, 9]
    """

    default = kwargs.get('default', None)

    for key in args:
        yield get(indexable, key, default=default)



def subdict(dct, include=(), exclude=()):
    """
        Return a dictionary that is a copy of the given one.

        All values in `include` are used as key to be copied to
         the resulting dictionary.

        You can also pass a list of key to exclude instead by setting
        `exclude`. But you can't use both `include` and `exclude`: if you do,
        `exclude will be ignored`

        Example:

        >>> subdict({1:None, 2: False, 3: True}, [1, 2])
        {1: None, 2: False}
        >>> subdict({1:None, 2: False, 3: True}, exclude=[1, 2])
        {3: True}

    """

    if include:
        return dict((k, v) for k, v in dct.iteritems() if k in include)

    return dict((k, v) for k, v in dct.iteritems() if k not in exclude)



# aliased for compat, but should probably be removed
first = lambda data, default=None: iget(data, 0, default)


def first_true(iterable, key=lambda x: x, default=None):
    """
        Return the first item of any iterable for which the key is True.

        By default the key is the entire element.

        If the iterable is empty, return the default value.
    """
    for x in iterable:
        if key(x):
            return x
    return default


def skip_duplicates(iterable, key=lambda x: x):
    """
        Returns a generator that will yield all objects from iterable, skipping
        duplicates.

        Duplicates are identified using the `key` function to calculate a
        unique fingerprint. This does not use natural equality, but the
        result use a set() to remove duplicates, so defining __eq__
        on your objects would have not effect.

        By default the fingerprint is the object itself,
        which ensure the functions works as-is with iterable of primitives
        such as int, str or tuple.

        :Example:

            >>> list(skip_duplicates([1, 2, 3, 4, 4, 2, 1, 3 , 4]))
            [1, 2, 3, 4]

        The return value of `key` MUST be hashable, which means for
        non hashable objects such as dict, set or list, you need to specify
        a a function that returns a hashable fingerprint.

        :Example:

            >>> list(skip_duplicates(([], [], (), [1, 2], (1, 2)), lambda x: tuple(x)))
            [[], [1, 2]]
            >>> list(skip_duplicates(([], [], (), [1, 2], (1, 2)), lambda x: (type(x), tuple(x))))
            [[], (), [1, 2], (1, 2)]

        For more complex types, such as custom classes, the default behavior
        is to remove nothing. You MUST provide a `key` function is you wish
        to filter those.

        :Example:

            >>> class Test(object):
                def __init__(self, foo='bar'):
                    self.foo = foo
                def __repr__(self):
                    return "Test('%s')" % self.foo
            ...
            >>> list(skip_duplicates([Test(), Test(), Test('other')]))
            [Test('bar'), Test('bar'), Test('other')]
            >>> list(skip_duplicates([Test(), Test(), Test('other')], lambda x: x.foo))
            [Test('bar'), Test('other')]

        See also :
            - strip_duplicates : a simpler, slower function that returns a list
                                 of elements with no duplicates. It accepts
                                 non hashable elements and honors __eq__.
          - remove_duplicates : remove duplicates from a list in place.
                                Most ressource efficient merthod.
    """
    fingerprints = set()

    try:
        for x in iterable:
            fingerprint = key(x)
            if fingerprint not in fingerprints:
                yield x
                fingerprints.add(fingerprint)
    except TypeError as e:
        try:
            hash(fingerprint)
        except TypeError:
            raise TypeError(
                "Calculating the key on one element resulted in a non hashable "
                "object of type '%s'. Change the 'key' parameter to a function "
                "that always, returns a hashable object. Hint : primitives "
                "like int, str or tuple, are hashable, dict, set and list are "
                "not. \nThe object that triggered the error was:\n%s" % (
                type(fingerprint), x)
            )
        else:
            raise



def strip_duplicates(iterable, equals=lambda x, y: x == y):
    """
        Return a list of elements from iterable, without duplicates.

        This uses equality to find duplicates, and will honor __eq__, but
        will not work on infinite iterables.

        :Examples:

            >>> strip_duplicates('fdjqkslfjdmkfdsqjkfmjqsdmlkfjqslkmfjsdklfl')
            ['f', 'd', 'j', 'q', 'k', 's', 'l', 'm']
            >>> strip_duplicates(([], [], (), [1, 2], (1, 2)))
            [[], (), [1, 2], (1, 2)]
            >>> strip_duplicates(([], [], (), [1, 2], (1, 2)), lambda x, y: tuple(x) == tuple(y))
            [[], [1, 2]]
            >>> class Test(object):
                def __init__(self, foo='bar'):
                    self.foo = foo
                def __repr__(self):
                    return "Test('%s')" % self.foo
                def __eq__(self, other):
                    return self.foo == other.foo
            >>> strip_duplicates([Test(), Test(), Test('other')])
            [Test('bar'), Test('other')]

        See also :
          - skip_duplicates : returns a generator yielding elements without
                              duplicates. Faster, works on infinite iterables,
                              but uses hashes instead of equality.
          - remove_duplicates : remove duplicates from a list in place.
                                Most ressource efficient merthod.
    """

    iterable = iter(iterable)

    res = []
    while True:

        try:
            elem = next(iterable)
        except StopIteration:
            break

        res.append(elem)

        iterable = iter([x for x in iterable if not equals(elem, x)])

    return res


def remove_duplicates(lst, equals=lambda x, y: x == y):
    """
        Removes duplicates from a list, in place.

        Works only with lists and modifies the list, but it's pretty ressource
        saving compared to other methods.

        See also :
          - skip_duplicates : returns a generator yielding elements without
                              duplicates. Faster, works on infinite iterables,
                              but uses hashes instead of equality.
          - strip_duplicates : a simpler, slower function that returns a list
                                 of elements with no duplicates. It accepts
                                 non hashable elements and honors __eq__.
    """

    if not isinstance(lst, list):
        raise TypeError('This function works only with lists.')

    i1 = 0
    l = (len(lst) - 1)

    while i1 < l:

        elem = lst[i1]

        i2 = i1 + 1
        while i2 <= l:
            if equals(elem, lst[i2]):
                del lst[i2]
                l -= 1
            i2 += 1

        i1 += 1

    return lst



KEY, PREV, NEXT = range(3)


class sset(MutableSet):
    """
        Set that preserves ordering.

        From http://code.activestate.com/recipes/576694/
    """

    def __init__(self, iterable=None):
        self.end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[PREV]
            curr[NEXT] = end[PREV] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:
            key, prev, next = self.map.pop(key)
            prev[NEXT] = next
            next[PREV] = prev

    def __iter__(self):
        end = self.end
        curr = end[NEXT]
        while curr is not end:
            yield curr[KEY]
            curr = curr[NEXT]

    def __reversed__(self):
        end = self.end
        curr = end[PREV]
        while curr is not end:
            yield curr[KEY]
            curr = curr[PREV]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = next(reversed(self)) if last else next(iter(self))
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, sset):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

    def __del__(self):
        self.clear()   # remove circular references



class Flattener(object):
    """
        Create a flattener that you can call on a deeply nested data
        structures to iterate over the items as it if it were a flat iterable.

        The flattener returns a generator that lazily yield the items and
        deals with up to hundred of levels of nesting (~800 on my machine,
        and you can control it with sys.setrecursionlimit).

        A default flattener named 'flatten' is available by default.

        :Example:

            a = []
            for i in range(10):
                a = [a, i]
            print(a)

            [[[[[[[[[[[], 0], 1], 2], 3], 4], 5], 6], 7], 8], 9]

            print(list(flatten(a)))

            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

        By default, it flattens all the types listed in
        Flattener.DEFAULT_FLATTEN_TYPES but you can pass you list via
        flatten_types while calling a Flatener instance.

        For ambigious types like dict, you can pass iterable_getters, a
        mapping type / callback letting you define how to extract items from
        each type.

        :Example:

            a = []
            for i in range(2):
                a = [a, i] + [{'a': 1., 'b': {'c': 3.}}]
            print(a)

            [[[], 0, {'a': 1.0, 'b': {'c': 3.0}}], 1, {'a': 1.0, 'b': {'c': 3.0}}]

            new_ft = Flattener.DEFAULT_FLATTEN_TYPES + (dict,)

            dico_flatten = Flattener(flatten_types=new_ft,
                                     iterable_getters={dict: lambda x: x.items()})

            print(list(dico_flatten(a)))

            [0, u'a', 1.0, u'b', u'c', 3.0, 1, u'a', 1.0, u'b', u'c', 3.0]

    """

    DEFAULT_FLATTEN_TYPES = (
        list,
        tuple,
        set,
        (x for x in ()).__class__,
        xrange,
        deque,
        MutableSet,
        # Sequence # warning, a string is a subclass of Sequence
    )


    def __init__(self, flatten_types=None, iterable_getters={}):
        self.flatten_types = flatten_types or self.DEFAULT_FLATTEN_TYPES
        self.iterable_getters = iterable_getters


    def should_flatten(self, obj):
        """
            Returns if the object should be flatten or not, checking if the
            objects is an instance of type listed in DEFAULT_FLATTEN_TYPES
            by default.
        """
        return isinstance(obj, self.flatten_types)


    def transform_iterable(self, obj):
        """
            Apply a pre-processing to an object before iterate on it. Can
            be useful for types such as dict on which you may want to call
            values() or items() before iteration.

            By defaut, it check if the object is an DIRECT instance (not
            a subclass) of any key in iterable_getters, passed in __init__
            and apply the transform.

            iterable_getter should be a mapping with types as key and
            transformation function as values, such as :

            {dict: lambda x: x.items()}

            iterable_getter default value is {}, making transform_iterable
            a noop.
        """
        if obj.__class__ in self.iterable_getters:
            return self.iterable_getters[obj.__class__](obj)
        return obj


    def __call__(self, iterable):
        """
            Returns a generator yieling items from a deeply nested iterable
            like it would be a flat one.
        """
        for e in iterable:
            if self.should_flatten(e):
                for f in self(self.transform_iterable(e)):
                    yield f
            else:
                yield e



flatten = Flattener()

