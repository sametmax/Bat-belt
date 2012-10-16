#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

__version__ = "0.1.1"

from strings import slugify, normalize
from structs import chunks, get, dmerge, OrderedSet
from objects import attr, import_from_path
from parallel import process, thread