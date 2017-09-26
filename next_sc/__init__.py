#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

import gi.repository
import os

gi.require_version('Gtk', '3.0')
gi.require_version('Gio', '2.0')
gi.require_version('AppStreamGlib', '1.0')


def get_resource_path():
    bsPath = os.path.dirname(__file__)
    return os.path.join(bsPath, "data")


def join_resource_path(path):
    return os.path.join(get_resource_path(), path)
