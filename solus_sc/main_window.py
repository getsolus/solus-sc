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
from .sidebar import ScSidebar
from gi.repository import Gtk, GLib


class ScMainWindow(Gtk.ApplicationWindow):

    groups_view = None
    main_layout = None
    sidebar = None
    stack = None

    def init_view(self):
        self.stack.set_visible_child_name("home")
        return False

    def on_mapped(self, w, udata=None):
        GLib.timeout_add(200, self.init_view)

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app)

        # Set up the headerbar. Because GNOME n stuff.
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        self.set_titlebar(headerbar)

        self.set_title("Software Center")

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(800, 600)

        self.stack = Gtk.Stack()
        # We'll add view switching later
        self.groups_view = ScGroupsView()

        # Main horizontal layout (Sidebar|VIEW)
        self.main_layout = Gtk.HBox(0)
        self.add(self.main_layout)

        self.sidebar = ScSidebar()
        self.main_layout.pack_start(self.sidebar, False, False, 0)
        self.main_layout.pack_start(self.stack, True, True, 0)

        # Dummy view for first time showing the application
        self.dummy_widget = Gtk.EventBox()
        self.stack.add_titled(self.dummy_widget, "empty", "empty")
        self.stack.add_titled(self.groups_view, "home", "Home")

        self.stack.set_visible_child_name("empty")
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP)

        self.connect("map-event", self.on_mapped)

        self.show_all()
