#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

import gi
try:
    gi.require_version('Snapd', '1')
except Exception as ex:
    print("Could not import Snapd: {}".format(ex))
    pass

try:
    gi.require_version('Ldm', '1.0')
except Exception as ex:
    print("Could not import Ldm: {}".format(ex))
