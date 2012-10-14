#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu


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

