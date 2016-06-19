#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

import locale


def sc_format_size(size):
    """ Get the *ibyte size (not megabyte.. 90s ended) format """
    labels = ["B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]

    for i, label in enumerate(labels):
        if size < 1000 or i == len(labels) - 1:
            return size, label
        size = float(size / 1000)


def sc_format_size_local(size, double_precision=False):
    """ Get the locale appropriate representation of the size """
    numeric, code = sc_format_size(size)
    fmt = "%.1f" if not double_precision else "%.2f"
    dlSize = "%s %s" % (locale.format(fmt, numeric, grouping=True), code)

    return dlSize
