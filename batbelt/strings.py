# -*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 nu

u"""
    A generic slugifier utility.

    Works out of the box for Latin-based scripts.

    Example:

        >>> from slugify import slugify
        >>> slugify(u"C'est Noël !")
        u'cest-noel'
        >>> slugify(u"C'est Noël !", separator="_")
        u'cest_noel'

    It will handle all unicode equivalences if (and only if) the optional
    unidecode library is installed.

    Example:

        >>> slugify(u"北亰")
        u'bei-jing'

    More about it:
      - http://en.wikipedia.org/wiki/Unicode_equivalence;
      - http://pypi.python.org/pypi/Unidecode.

    If you do have unidecode installed, but wish not to use it, use the
    unicodedata_slugify fonction:

        >>> slugify(u"Héllø Wörld") # slugify() uses unidecode if it can
        u'hello-world'
        >>> unicodedata_slugify(u"Héllø Wörld") # this will more limited
        u'hell-world'

    In case you wish to keep the non ASCII characters "as-is", use
    unicode_slugify():

    >>> print unicode_slugify(u"C'est Noël !")
    cest-noël

"""

import re
import unicodedata

__all__ = ['unicode_slugify', 'unicodedata_slugify', 'unidecode_slugify',
           'unicodedata_normalize', 'unidecode_normalize', 'slugify', 'normalize']


def unicode_slugify(string, separator=r'-'):
    ur"""
    Slugify a unicode string using to normalize the string, but without trying
    to convert or strip non ASCII characters.

    Example:

        >>> print unicode_slugify(u"Héllø Wörld")
        héllø-wörld
        >>> unidecode_slugify(u"Bonjour, tout l'monde !", separator="_")
        u'bonjour_tout_lmonde'
        >>> unidecode_slugify(u"\tStuff with -- dashes and...   spaces   \n")
        u'stuff-with-dashes-and-spaces'
    """

    string = re.sub(r'[^\w\s' + separator + ']', '', string, flags=re.U)
    string = string.strip().lower()
    return unicode(re.sub(r'[' + separator + '\s]+',
                   separator, string, flags=re.U))


def unicodedata_slugify(string, separator=r'-'):
    ur"""
    Slugify a unicode string using unicodedata to normalize the string.

    Example:

        >>> unicodedata_slugify(u"Héllø Wörld")
        u'hell-world'
        >>> unidecode_slugify(u"Bonjour, tout l'monde !", separator="_")
        u'bonjour_tout_lmonde'
        >>> unidecode_slugify(u"\tStuff with -- dashes and...   spaces   \n")
        u'stuff-with-dashes-and-spaces'
    """

    string = unicodedata.normalize('NFKD', string).encode('ascii', 'ignore')
    string = re.sub(r'[^\w\s' + separator + ']', '', string).strip().lower()
    return unicode(re.sub(r'[' + separator + '\s]+', separator, string))


def unidecode_slugify(string, separator=r'-'):
    ur"""
    Slugify a unicode string using unidecode to normalize the string.

    Example:

        >>> unidecode_slugify(u"Héllø Wörld")
        u'hello-world'
        >>> unidecode_slugify(u"Bonjour, tout l'monde !", separator="_")
        u'bonjour_tout_lmonde'
        >>> unidecode_slugify(u"\tStuff with -- dashes and...   spaces   \n")
        u'stuff-with-dashes-and-spaces'
    """

    string = unidecode.unidecode(string)
    string = re.sub(r'[^\w\s' + separator + ']', '', string).strip().lower()
    return unicode(re.sub(r'[' + separator + '\s]+', separator, string))


def unicodedata_normalize(string):
    return unicodedata.normalize('NFKD', string).encode('ascii', 'ignore')


def unidecode_normalize(string):
    return unidecode.unidecode(string)


try:
    import unidecode
    slugify = unidecode_slugify
    normalize = unidecode_normalize
except ImportError:
    slugify = unicodedata_slugify
    normalize = unicodedata_normalize


if __name__ == "__main__":
    import doctest
    doctest.testmod()
