# -*- coding: utf-8 -*-
#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4 nu

r"""

    Various tools to manipulate strings. Features tools to normalize and
    slugify strings. Also some ways to escape HTML and a JSON serializer
    that deals with datetime objects.

    Here is an example of the generic slugifier utility (as for 'normalize',
    'escape_html', 'unescape_html' and "json_dumps" are pretty straightforward
    and don't need that much of an explanation. Ok, it's just because I'm
    too lazy to write it down really).

    Works out of the box for Latin-based scripts.

    Example:

        >>> from strings import slugify
        >>> slugify(u"C'est No\xebl !")
        u'cest-noel'
        >>> slugify(u"C'est No\xebl !", separator="_")
        u'cest_noel'

    It will handle all unicode equivalences if (and only if) the optional
    unidecode library is installed.

    Example:

        >>> slugify(u"\u5317\u4eb0")
        u'bei-jing'

    More about it:
      - http://en.wikipedia.org/wiki/Unicode_equivalence;
      - http://pypi.python.org/pypi/Unidecode.

    If you do have unidecode installed, but wish not to use it, use the
    unicodedata_slugify fonction:

        >>> slugify(u"H\xe9ll\xf8 W\xc3\xb6rld") # slugify() uses unidecode if it can
        u'hello-world'
        >>> unicodedata_slugify(u"H\xe9ll\xf8 W\xc3\xb6rld") # this will more limited
        u'hell-world'

    In case you wish to keep the non ASCII characters "as-is", use
    unicode_slugify():

    >>> print unicode_slugify(u"C'est No\xebl !")
    cest-no\xebl

"""

import re
import os
import codecs
import json
import unicodedata

from datetime import datetime, timedelta, date, time
from xml.sax.saxutils import escape, unescape

from utils import CLASSIC_DATETIME_FORMAT, CLASSIC_DATETIME_PATTERN



def unicode_slugify(string, separator=r'-'):
    r"""
    Slugify a unicode string using to normalize the string, but without trying
    to convert or strip non ASCII characters.

    Example:

        >>> print unicode_slugify(u"H\xe9ll\xf8 W\xc3\xb6rld")
        h\xe9ll\xf8-w\xc3\xb6rld
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
    r"""
    Slugify a unicode string using unicodedata to normalize the string.

    Example:

        >>> unicodedata_slugify(u"H\xe9ll\xf8 W\xc3\xb6rld")
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
    r"""
    Slugify a unicode string using unidecode to normalize the string.

    Example:

        >>> unidecode_slugify(u"H\xe9ll\xf8 W\xc3\xb6rld")
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
    r"""
        Returns a new string withou non ASCII characters, trying to replace
        them with their ASCII closest counter parts when possible.

        :Example:

            >>> normalize(u"H\xe9ll\xf8 W\xc3\xb6rld")
            'Hell World'


        This version use unicodedata and provide limited yet
        useful results.
    """
    return unicodedata.normalize('NFKD', string).encode('ascii', 'ignore')


def unidecode_normalize(string):
    r"""
        Returns a new string withou non ASCII characters, trying to replace
        them with their ASCII closest counter parts when possible.

        :Example:

            >>> normalize(u"H\xe9ll\xf8 W\xc3\xb6rld")
            'Hello World'

        This version use unidecode and provide enhanced results.
    """
    return unidecode.unidecode(string)


try:
    import unidecode
    slugify = unidecode_slugify
    normalize = unidecode_normalize
except ImportError:
    slugify = unicodedata_slugify
    normalize = unicodedata_normalize


def escape_html(text, additional_escape={'"': "&quot;", "'": "&apos;"}):
    """
        Turn HTML tag caracters into HTML entities.


        Example:

            >>> escape_html("<strong>Ben & Jelly's !</strong>")
            '&lt;strong&gt;Ben &amp; Jelly&apos;s !&lt;/strong&gt;'

    """
    return escape(text, additional_escape)


def unescape_html(text, additional_escape={"&quot;": '"', "&apos;": "'"}):
    """
        Turn HTML tag entities into ASCII caracters.

        Example:

            >>> unescape_html('&lt;strong&gt;Ben &amp; Jelly&apos;s !&lt;/strong&gt;')
            "<strong>Ben & Jelly's !</strong>"
    """
    return unescape(text, additional_escape)



class JSONEncoder(json.JSONEncoder):
    """
        Json encoder with date and time handling.

        You should use naive datetime only. If you have timezone information,
        store them in a separate field.
    """


    DATETIME_FORMAT = CLASSIC_DATETIME_FORMAT
    DATE_FORMAT, TIME_FORMAT = DATETIME_FORMAT.split()
    TIMEDELTA_FORMAT = "timedelta(seconds='%s')"


    def __init__(self, datetime_format=None, date_format=None, time_format=None,
                timedelta_format=None, *args, **kwargs):

        self.datetime_format = datetime_format or self.DATETIME_FORMAT
        self.date_format = date_format or self.DATE_FORMAT
        self.time_format = time_format or self.TIME_FORMAT
        self.timedelta_format = timedelta_format or self.TIMEDELTA_FORMAT

        super(JSONEncoder, self).__init__(self, *args, **kwargs)


    def default(self, obj):

        if isinstance(obj, datetime):
            return obj.strftime(self.datetime_format)

        if isinstance(obj, date):
            return obj.strftime(self.date_format)

        if isinstance(obj, time):
            return obj.strftime(self.time_format)

        if isinstance(obj, timedelta):
            return self.timedelta_format % obj.total_seconds()

        return json.JSONEncoder.default(self, obj)



class JSONDecoder(json.JSONDecoder):
    """
        Json decoder that decode JSON encoded with JSONEncoder
    """

    DATETIME_PATTERN = CLASSIC_DATETIME_PATTERN
    DATE_PATTERN, TIME_PATTERN = DATETIME_PATTERN.split()
    TIMEDELTA_PATTERN = r"timedelta\(seconds='(?P<seconds>\d+(?:\.\d+)*)'\)"


    def __init__(self, datetime_pattern=None, date_pattern=None,
                time_pattern=None, timedelta_pattern=None, datetime_format=None,
                date_format=None, time_format=None, *args, **kwargs):

        self.datetime_format = datetime_format or JSONEncoder.DATETIME_FORMAT
        self.date_format = date_format or JSONEncoder.DATE_FORMAT
        self.time_format = time_format or JSONEncoder.TIME_FORMAT

        self.datetime_pattern = re.compile(datetime_pattern or self.DATETIME_PATTERN)
        self.date_pattern = re.compile(date_pattern or self.DATE_PATTERN)
        self.time_pattern = re.compile(time_pattern or self.TIME_PATTERN)
        self.timedelta_pattern = re.compile(timedelta_pattern or self.TIMEDELTA_PATTERN)

        super(JSONDecoder, self).__init__(object_pairs_hook=self.object_pairs_hook,
                                          *args, **kwargs)

    def object_pairs_hook(self, obj):
        return dict((k, self.decode_on_match(v)) for k, v in obj)


    def decode_on_match(self, obj):
        """
            Try to match the string, and if it fits any date format,
            parse it and returns a Python object.
        """

        string = unicode(obj)

        match = re.search(self.datetime_pattern, string)
        if match:
            return datetime.strptime(match.string, self.datetime_format)

        match = re.search(self.date_pattern, string)
        if match:
            return datetime.strptime(match.string, self.date_format).date()

        match = re.search(self.time_pattern, string)
        if match:
            return datetime.strptime(match.string, self.time_format).time()

        match = re.search(self.timedelta_pattern, string)
        if match:
            return timedelta(seconds=float(match.groupdict()['seconds']))

        return obj


def json_dumps(data, datetime_format=None, date_format=None, time_format=None,
                timedelta_format=None, *args, **kwargs):
    r"""
        Same as Python's json.dumps but also serialize datetime, date, time
        and timedelta.

        Example:
            >>> import datetime
            >>> json_dumps({'test': datetime.datetime(2000, 1, 1, 1, 1, 1)})
            '{"test": "2000-01-01 01:01:01.000000"}'
            >>> json_dumps({'test': datetime.date(2000, 1, 1)})
            '{"test": "2000-01-01"}'
            >>> json_dumps({'test': datetime.time(1, 1, 1)})
            '{"test": "01:01:01.000000"}'
            >>> json_dumps({'test': datetime.timedelta(1, 1)})
            '{"test": "timedelta(seconds=\'86401.0\')"}'
            >>> json_dumps({u'test': datetime.timedelta(1, 1), u'a': [1, 2]})
            '{"test": "timedelta(seconds=\'86401.0\')", "a": [1, 2]}'

    """
    return JSONEncoder(datetime_format, date_format, time_format,
                       timedelta_format, *args, **kwargs).encode(data)


def json_loads(string, datetime_pattern=None, date_pattern=None,
                time_pattern=None, timedelta_pattern=None, datetime_format=None,
                date_format=None, time_format=None, *args, **kwargs):
    r"""
        Same as Python's json.loads, but handles formats from batbelt.json_dumps
        which are currently mainly date formats.

        Example:

            >>> json_loads('{"test": "2000-01-01 01:01:01.000000"}')
            {u'test': datetime.datetime(2000, 1, 1, 1, 1, 1)}
            >>> json_loads('{"test": "2000-01-01"}')
            {u'test': datetime.date(2000, 1, 1)}
            >>> json_loads('{"test": "01:01:01.000000"}')
            {u'test': datetime.time(1, 1, 1)}
            >>> json_loads('{"test": "timedelta(seconds=\'86401.0\')"}')
            {u'test': datetime.timedelta(1, 1)}
            >>> json_loads('{"test": "timedelta(seconds=\'86401.0\')", "a": [1, 2]}')
            {u'test': datetime.timedelta(1, 1), u'a': [1, 2]}

    """
    return JSONDecoder(datetime_pattern, date_pattern, time_pattern,
                       timedelta_pattern, datetime_format, date_format,
                       time_format, *args, **kwargs).decode(string)


def template(tpl, context):
    """
      Use the given a template file, call .format() on it's content,
      and returns it as a string.

      Template file can be a path or a file like object.
    """

    try:
        tpl = open(tpl)
    except TypeError:
        pass

    return tpl.read().format(**context)


def render(tpl, context, target):
    """
      Render the template and write the result in a file.

      Template and target files can be a path or a file like objects.
    """

    try:
        target = open(target, 'w')
    except TypeError:
        pass

    res = template(tpl, context)
    target.write(res)

    target.close()


def write(path, *args, **kwargs):
    """
        Try to write to the file at `path` the values passed as `args` as lines.

        It will attempt decoding / encoding and casting automatically each value
        to a string.

        This is an utility function : its slow and doesn't consider edge cases,
        but allow to do just what you want most of the time in one line.

        :Example:

            s = '/tmp/test'
            write(s, 'test', '\xe9', 1, ['fdjskl'])
            print open(s).read()
            test
            \xe9
            1
            ['fdjskl']

        You can optionally pass :

        mode : among 'a', 'w', which default to 'w'. Binary mode is forced.
        encoding : which default to utf8 and will condition decoding AND encoding
        errors : what to do when en encoding error occurs : 'replace' by default,
                which replace faulty caracters with '?'

        You can pass string or unicode as *args, but if you pass strings,
        make sure you pass them with the same encoding you wish to write to
        the file.
    """

    mode = kwargs.get('mode', 'w')
    encoding = kwargs.get('encoding', 'utf8')
    errors = kwargs.get('encoding', 'replace')

    with codecs.open(path, mode=mode, encoding=encoding, errors=errors) as f:

        for line in args:

            if isinstance(line, str):
                line = line.decode(encoding, errors)

            if not isinstance(line, unicode):
                line = repr(line)

            f.write(line + os.linesep)



if __name__ == "__main__":
    import doctest
    doctest.testmod()

