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


class ScPlaceholderBox(Gtk.VBox):
    """ So we don't show empty boxes :) """

    def __init__(self):
        Gtk.VBox.__init__(self)
        lab = Gtk.Label("Sorry, this page is not yet implemented.")
        self.add(lab)


class ScMainWindow(Gtk.ApplicationWindow):

    groups_view = None
    main_layout = None
    sidebar = None
    stack = None
    sidebar_revealer = None

    def init_view(self):
        self.stack.set_visible_child_name("home")
        self.sidebar_revealer.set_reveal_child(True)
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
        self.get_style_context().add_class("solus-sc")

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(800, 600)

        self.stack = Gtk.Stack()
        self.stack.get_style_context().add_class("main-view")
        # We'll add view switching later
        self.groups_view = ScGroupsView()

        # Main horizontal layout (Sidebar|VIEW)
        self.main_layout = Gtk.HBox(0)
        self.add(self.main_layout)

        self.sidebar = ScSidebar(self.stack)
        self.sidebar_revealer = Gtk.Revealer()
        self.sidebar_revealer.add(self.sidebar)
        self.sidebar_revealer.set_reveal_child(False)
        self.main_layout.pack_start(self.sidebar_revealer, False, False, 0)
        self.main_layout.pack_start(self.stack, True, True, 0)

        # Dummy view for first time showing the application
        self.dummy_widget = Gtk.EventBox()

        # Supported views
        self.stack.add_titled(self.dummy_widget, "empty", "empty")
        self.stack.add_titled(self.groups_view, "home", "Home")

        # These guys aren't yet implemented
        self.stack.add_titled(ScPlaceholderBox(), "updates", "Updates")
        self.stack.add_titled(ScPlaceholderBox(), "installed", "Installed")
        self.stack.add_titled(ScPlaceholderBox(), "3rd-party", "Third Party")
        self.stack.add_titled(ScPlaceholderBox(), "settings", "Settings")

        # set up intro animation
        self.stack.set_visible_child_name("empty")
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP)
        revel = Gtk.RevealerTransitionType.SLIDE_RIGHT
        self.sidebar_revealer.set_transition_type(revel)

        self.connect("map-event", self.on_mapped)

        self.show_all()
