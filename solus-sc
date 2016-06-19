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

import sys
from solus_sc.application import ScApplication
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject, Gdk


if __name__ == "__main__":
    DBusGMainLoop(set_as_default=True)
    GObject.threads_init()
    Gdk.threads_init()
    app = ScApplication()
    app.run(sys.argv)
