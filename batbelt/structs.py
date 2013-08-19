#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu


from collections import MutableSet, deque

from itertools import islice, chain


__all__ = ['chunks', 'dmerge', 'get', 'window', 'dswap', 'subdict', 'first',
           'first_true', 'sset']


def chunks(seq, chunksize, process=iter):
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


def unpack(dct, *args, **kwargs):
    """
        Return an generator with the values for the given keys or
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

    """

    default = kwargs.get('default', None)

    for key in args:
        yield dct.get(key, default)



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


def first(iterable, default=None):
    """
        Return the first item of any iterable. If the iterable is empty,
        return the default value.
    """
    for x in iterable:
        return x
    return default


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


