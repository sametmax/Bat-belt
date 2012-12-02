#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu


from collections import MutableSet

from itertools import islice, chain


all = ['chunks', 'dmerge', 'get']


def chunks(seq, chunksize, process=iter):
    """ Yields items from an iterator in iterable chunks."""
    it = iter(seq)
    while True:
        yield process(chain([it.next()], islice(it, chunksize - 1)))


def dmerge(d1, d2):
    """
        Create a new dictionary being the merge of the two passed as a
        parameter.

        The keys in the second one erases the keys in the first one.
    """
    d = {}
    d.update(d1)
    d.update(d2)
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


def subdict(dct, include=(), exclude=()):
    """
        Return a dictionary that is a copy of the given one.

        All tvalues in `include` are used as key to be copied to
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


