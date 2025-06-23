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

from .appsystem import AppSystem
from .groups import ScGroupsView
from .installed_view import ScInstalledView
from .sidebar import ScSidebar
from .updates_view import ScUpdatesView
from .basket import BasketView
from .search import ScSearchView
from .thirdparty import ThirdPartyView
from .settings_view import ScSettingsView
from gi.repository import Gtk, Gdk, GLib, Gio
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
    installed_view = None
    updates_view = None
    search_view = None
    third_party = None
    settings_view = None

    prev_button = None

    app = None

    # Default open mode
    mode_open = None
    action_bar = None
    did_map_once = False

    def show_updates(self):
        """ Switch to updates view """
        self.sidebar.preselect_row("updates")

    def show_search(self):
        """ Switch to search view """
        self.sidebar.preselect_row("search")

    def do_delete_event(self, event, udata=None):
        """ For now just propagate the event """
        return False

    def do_back(self):
        """ Handle back navigation """
        nom = self.stack.get_visible_child_name()
        if nom == "installed":
            self.installed_view.handle_back()
        elif nom == "home":
            self.groups_view.handle_back()
        elif nom == "search":
            self.search_view.handle_back()
        else:
            print("Shouldn't be happening boss")

    def handle_back(self, btn, udata=None):
        self.do_back()

    def set_can_back(self, can_back):
        self.prev_button.set_sensitive(can_back)

    def update_back(self, nom):
        """ Update back navigation """
        sensitive = False
        if nom == "installed":
            sensitive = self.installed_view.can_back()
        elif nom == "home":
            sensitive = self.groups_view.can_back()
        elif nom == "search":
            sensitive = self.search_view.can_back()
        self.set_can_back(sensitive)

    def init_children(self):
        self.installed_view.init_view()

        # If we're not allowed to refresh on metered connections, only
        # show the cached results on startup
        settings = Gio.Settings.new("com.solus-project.software-center")
        mon = Gio.NetworkMonitor.get_default()
        if mon is not None:
            can_net = settings.get_boolean("update-on-metered")
            if not can_net and mon.get_network_metered():
                self.updates_view.init_view()
                return

        GLib.idle_add(self.updates_view.external_refresh)

    def init_view(self):
        """ Our first ever show """
        self.sidebar_revealer.set_reveal_child(True)
        self.sidebar.preselect_row(self.mode_open)
        self.stack.set_visible_child_name(self.mode_open)
        return False

    def on_mapped(self, w, udata=None):
        if self.did_map_once:
            return
        self.did_map_once = True
        GLib.timeout_add(200, self.init_view)

    def on_button_press_event(self, widget, event):
        if event.button == 8:  # Back button
            self.do_back()

    def on_key_press_event(self, widget, event):
        # check event modifiers
        ctrl = (event.state & Gdk.ModifierType.CONTROL_MASK)

        # check if search view hotkey was pressed
        if ctrl and event.keyval == Gdk.keyval_from_name('f'):
            self.show_search()

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app)

        self.app = app
        self.mode_open = "home"
        self.appsystem = AppSystem()

        self.set_icon_name("system-software-install")
        # Set up the headerbar. Because GNOME n stuff.
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        self.set_titlebar(headerbar)

        self.prev_button = Gtk.Button.new_from_icon_name(
            "go-previous-symbolic", Gtk.IconSize.BUTTON)
        headerbar.pack_start(self.prev_button)
        self.prev_button.connect("clicked", self.handle_back)

        # Window title
        self.set_title(_("Software Center"))
        self.get_style_context().add_class("solus-sc")

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(950, 650)

        self.stack = Gtk.Stack()
        self.stack.get_style_context().add_class("main-view")
        self.set_can_back(False)
        # We'll add view switching later
        try:
            self.init_first()
        except Exception as e:
            print(e)
            sys.exit(1)

    def init_first(self):
        self.basket = BasketView(self)
        self.groups_view = ScGroupsView(self)

        # Main horizontal layout (Sidebar|VIEW)
        self.main_layout = Gtk.HBox(0)
        self.add(self.main_layout)

        self.sidebar = ScSidebar(self, self.stack)
        self.sidebar_revealer = Gtk.Revealer()
        self.sidebar_revealer.add(self.sidebar)
        self.sidebar_revealer.set_reveal_child(False)
        self.main_layout.pack_start(self.sidebar_revealer, False, False, 0)
        sep = Gtk.Separator()
        sep.set_orientation(Gtk.Orientation.VERTICAL)
        sep.get_style_context().add_class("sidebar-separator")
        self.main_layout.pack_start(sep, False, False, 0)

        tmpvbox = Gtk.VBox(0)
        tmpvbox.pack_start(self.stack, True, True, 0)
        tmpvbox.pack_start(self.basket, False, False, 0)
        self.main_layout.pack_start(tmpvbox, True, True, 0)

        # Dummy view for first time showing the application
        self.dummy_widget = Gtk.EventBox()

        # Supported views
        self.stack.add_titled(self.dummy_widget, "empty", "empty")
        # Main view, primary view, when opening the software center
        self.stack.add_titled(self.groups_view, "home", _("Home"))
        self.updates_view = ScUpdatesView(self.basket, self.appsystem)
        # The page where updates are display
        self.stack.add_titled(self.updates_view, "updates", _("Updates"))

        # Package view for installed page
        self.installed_view = ScInstalledView(self, self.basket, self.appsystem)

        # This page shows the locally instaleld items
        self.stack.add_titled(self.installed_view, "installed", _("Installed"))

        self.third_party = ThirdPartyView(self)
        # Software made available from outside the Solus software repos
        self.stack.add_titled(self.third_party, "3rd-party", _("Third Party"))

        # Search view
        self.search_view = ScSearchView(self)
        # The search page
        self.stack.add_titled(self.search_view, "search", _("Search"))

        self.settings_view = ScSettingsView(self)
        # The settings page
        self.stack.add_titled(self.settings_view, "settings", _("Settings"))

        # set up intro animation
        self.stack.set_visible_child_name("empty")
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP)
        revel = Gtk.RevealerTransitionType.SLIDE_RIGHT
        self.sidebar_revealer.set_transition_type(revel)

        self.connect("map-event", self.on_mapped)
        self.connect("button-press-event", self.on_button_press_event)
        self.connect("key-press-event", self.on_key_press_event)

        t = threading.Thread(target=self.init_children)
        t.start()

        self.show_all()
