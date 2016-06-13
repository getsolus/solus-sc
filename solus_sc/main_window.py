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

from .appsystem import AppSystem
from .groups import ScGroupsView
from .package_view import ScPackageView
from .sidebar import ScSidebar
from .updates_view import ScUpdatesView
from .basket import BasketView
from gi.repository import Gtk, GLib
import sys
import threading


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
    appsystem = None

    # Pages
    package_view = None
    updates_view = None

    prev_button = None

    def handle_back(self, btn, udata=None):
        """ Handle back navigation """
        nom = self.stack.get_visible_child_name()
        if nom == "installed":
            self.package_view.handle_back()
        elif nom == "home":
            self.groups_view.handle_back()
        else:
            print("Shouldn't be happening boss")

    def init_children(self):
        self.package_view.init_view()
        self.updates_view.init_view()

    def init_view(self):
        self.stack.set_visible_child_name("home")
        self.sidebar_revealer.set_reveal_child(True)
        t = threading.Thread(target=self.init_children)
        t.start()
        return False

    def on_mapped(self, w, udata=None):
        GLib.timeout_add(200, self.init_view)

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app)

        self.appsystem = AppSystem()

        # !!HAX!! - we're missing a .desktop file atm. shush.
        self.set_icon_name("system-software-install")
        # Set up the headerbar. Because GNOME n stuff.
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        self.set_titlebar(headerbar)

        self.prev_button = Gtk.Button.new_from_icon_name(
            "go-previous-symbolic", Gtk.IconSize.BUTTON)
        headerbar.pack_start(self.prev_button)
        self.prev_button.connect("clicked", self.handle_back)

        self.set_title("Software Center")
        self.get_style_context().add_class("solus-sc")

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(800, 600)

        self.stack = Gtk.Stack()
        self.stack.get_style_context().add_class("main-view")
        # We'll add view switching later
        try:
            self.init_first()
        except Exception as e:
            print(e)
            sys.exit(1)

    def init_first(self):
        self.groups_view = ScGroupsView()

        self.basket = BasketView(None, None)

        # Main horizontal layout (Sidebar|VIEW)
        self.main_layout = Gtk.HBox(0)
        self.add(self.main_layout)

        self.sidebar = ScSidebar(self.stack)
        self.sidebar_revealer = Gtk.Revealer()
        self.sidebar_revealer.add(self.sidebar)
        self.sidebar_revealer.set_reveal_child(False)
        self.main_layout.pack_start(self.sidebar_revealer, False, False, 0)
        sep = Gtk.Separator()
        sep.set_orientation(Gtk.Orientation.VERTICAL)
        self.main_layout.pack_start(sep, False, False, 0)
        self.main_layout.pack_start(self.stack, True, True, 0)

        # Dummy view for first time showing the application
        self.dummy_widget = Gtk.EventBox()

        # Supported views
        self.stack.add_titled(self.dummy_widget, "empty", "empty")
        self.stack.add_titled(self.groups_view, "home", "Home")
        self.updates_view = ScUpdatesView(self.basket)
        self.stack.add_titled(self.updates_view, "updates", "Updates")

        # Package view for installed page
        self.package_view = ScPackageView(self.basket, self.appsystem)

        # These guys aren't yet implemented
        self.stack.add_titled(self.package_view, "installed", "Installed")
        self.stack.add_titled(ScPlaceholderBox(), "3rd-party", "Third Party")
        self.stack.add_titled(ScPlaceholderBox(), "settings", "Settings")
        self.stack.add_titled(ScPlaceholderBox(), "basket", "Basket")

        # set up intro animation
        self.stack.set_visible_child_name("empty")
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP)
        revel = Gtk.RevealerTransitionType.SLIDE_RIGHT
        self.sidebar_revealer.set_transition_type(revel)

        self.connect("map-event", self.on_mapped)

        self.show_all()
