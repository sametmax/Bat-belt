#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu


__version__ = "0.5.2"

from strings import (slugify, normalize, escape_html,
                     unescape_html, json_dumps, json_loads)
from structs import (chunks, get, dmerge, sset, dswap, window,
                     subdict, iget, flatten, skip_duplicates)
from objects import attr, import_from_path, Null
from utils import to_timestamp
from hack import decorator_with_args
