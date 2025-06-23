#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2020 Solus
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
        size = float(size / 1024)


def sc_format_size_local(size, double_precision=False):
    """ Get the locale appropriate representation of the size """
    numeric, code = sc_format_size(size)
    fmt = "%.1f" if not double_precision else "%.2f"
    dlSize = "%s %s" % (locale.format_string(fmt, numeric, grouping=True), code)

    return dlSize


developmentComponents = [
    "system.devel",
    "programming.devel"
]


def is_package_devel(pkg):
    """ For filtering development packages """
    if str(pkg.name).endswith("-devel"):
        return True
    if not pkg.partOf:
        return False
    return str(pkg.partOf) in developmentComponents


def is_package_debug(pkg):
    """ For filtering debug packages """
    if str(pkg.name).endswith("-dbginfo"):
        return True
    if not pkg.partOf:
        return False
    return str(pkg.partOf) == "debug"
