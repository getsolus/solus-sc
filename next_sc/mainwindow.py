#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk
import sys
from plugins.native import get_native_plugin
from plugins.snapd import SnapdPlugin

class MainWindow(Gtk.ApplicationWindow):

    prev_button = None

    # parent app
    app = None

    # Default open mode
    mode_open = None

    # Our next_sc plugin set
    plugins = None

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app)

        self.app = app
        self.mode_open = "home"

        self.set_icon_name("system-software-install")
        # Set up the headerbar. Because GNOME n stuff.
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        self.set_titlebar(headerbar)

        self.prev_button = Gtk.Button.new_from_icon_name(
            "go-previous-symbolic", Gtk.IconSize.BUTTON)
        headerbar.pack_start(self.prev_button)

        # Window title
        self.set_title(_("Software Center"))

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(950, 650)

        self.init_plugins()

        try:
            self.init_first()
        except Exception as e:
            print(e)
            sys.exit(1)

    def init_plugins(self):
        """ Take care of setting up our plugins """
        self.plugins = []
        snap = None
        try:
            snap = SnapdPlugin()
        except Exception as e:
            print("snapd support unavailable on this system: {}".format(e))
            snap = None

        if snap is not None:
            self.plugins.append(snap)

        osPlugin = get_native_plugin()
        if osPlugin is not None:
            self.plugins.insert(0, osPlugin)
        else:
            print("WARNING: Unsupported OS, native packaging unavailable!")

    def init_first(self):
        """ TODO: Anything vaguely useful. """
        self.show_all()
