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


from gi.repository import GObject
from .backend import EopkgAssistService
import dbus.mainloop
import sys
import os


if __name__ == '__main__':
    if os.geteuid() != 0:
        sys.stderr.write("Need to be root to run eopkg_assist")
        sys.exit(1)
    dbus.mainloop.glib.threads_init()
    loop = GObject.MainLoop()
    try:
        service = EopkgAssistService(loop)
        loop.run()
    except Exception as e:
        print(e)
    finally:
        loop.quit()
    sys.exit(0)
