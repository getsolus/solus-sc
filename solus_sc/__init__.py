#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

import gi.repository
gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')

import locale

# Helper for formatting sizes
def sc_format_size(size):
    labels = ["B", "KiB", "MiB", "GiB", "PiB", "EiB", "ZiB", "YiB"]

    for i, label in enumerate(labels):
        if size < 1000 or i == len(labels) - 1:
            return size, label
        size = float(size / 1024)

def sc_format_size_local(size, double_precision=False):
    numeric, code = sc_format_size(size)
    fmt = "%.1f" if not double_precision else "%.2f"
    dlSize = "%s %s" % (locale.format(fmt, numeric, grouping=True), code)

    return dlSize
