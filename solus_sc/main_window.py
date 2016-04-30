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

from .groups import ScGroupsView
from gi.repository import Gtk


class ScMainWindow(Gtk.ApplicationWindow):

    groups_view = None

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app)

        # Set up the headerbar. Because GNOME n stuff.
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        self.set_titlebar(headerbar)

        self.set_title("Software Center")

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(800, 600)

        # We'll add view switching later
        self.groups_view = ScGroupsView()

        self.add(self.groups_view)

        self.show_all()
