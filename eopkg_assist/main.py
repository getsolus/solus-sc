#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#


from gi.repository import GObject
from .backend import EopkgAssistService
import dbus.mainloop
import sys


if __name__ == '__main__':
    GObject.threads_init()
    dbus.mainloop.glib.threads_init()
    loop = GObject.MainLoop()
    try:
        service = EopkgAssistService(loop)
        loop.run()
    except Exception, e:
        print e
    finally:
        loop.quit()
    sys.exit(0)
