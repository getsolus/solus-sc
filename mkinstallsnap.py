#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

import gi
gi.require_version('Snapd', '1')
from gi.repository import Snapd as snapd


def snapdDemo():
    cl = snapd.Client()
    cl.connect_sync()

    flags = snapd.InstallFlags.NONE # CLASSIC, DEVMODE, DANGEROUS, JAILMODE
    name = "ohmygiraffe"
    channel = None  # default channel
    revision = None  # default revision
    progress_callback = None
    cl.install2_sync(flags, name, channel, revision, progress_callback, None, None)


if __name__ == "__main__":
    snapdDemo()
