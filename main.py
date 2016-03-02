#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py - Entry point
#  
#  Copyright 2014 Ikey Doherty <ikey.doherty@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#
import sys
sys.path.append("/usr/lib/solus-sc")

import gi.repository
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, Gio
from dbus.mainloop.glib import DBusGMainLoop
import sys

from interface import SSCWindow

class SSCApp(Gtk.Application):

    app_win = None

    def __init__(self):
        Gtk.Application.__init__(self, application_id="com.solus_project.SSC",
            flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        if self.app_win is None:
            self.app_win = SSCWindow(self)
        self.app_win.present()

if __name__ == "__main__":
    DBusGMainLoop(set_as_default=True)
    GObject.threads_init()
    app = SSCApp()
    ex = app.run(sys.argv)
    sys.exit(ex)
