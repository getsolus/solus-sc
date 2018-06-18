#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from xng.application import ScApplication
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GObject, Gdk
import gettext
import sys


# Fix broken CTRL+C's and whatnot.
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)


def main():
    global setproctitle

    # Ensure a valid consistent process names
    try:
        from setproctitle import setproctitle
        setproctitle("solus-sc")
    except Exception as ex:
        print("Unable to set proc title - cosmetic, not fatal.")
        print(ex)

    DBusGMainLoop(set_as_default=True)
    GObject.threads_init()
    Gdk.threads_init()
    app = ScApplication()
    app.run(sys.argv)


if __name__ == "__main__":
    gettext.install("solus-sc", "/usr/share/locale")
    main()
