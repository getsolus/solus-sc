#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk, GObject, GLib
from .appsystem import AppSystem
from xng.plugins.base import PopulationFilter


class ScMainWindow(Gtk.ApplicationWindow):

    # Headerbar
    hbar = None
    search_button = None

    # Search bits
    search_revealer = None
    search_bar = None
    search_entry = None

    mode_open = None

    # Global AppSystem instance, handed to plugins
    appsystem = None

    search_idle_timeout = 0

    resolutions = [
        (1024, 576),
        (1156, 648),
        (1280, 760),
    ]

    def __init__(self, app):
        Gtk.Window.__init__(self, application=app)
        self.pick_resolution()
        self.build_headerbar()

        # Get main layout sorted
        self.layout = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.add(self.layout)

        self.build_search_bar()
        self.get_style_context().add_class("solus-sc")

        self.init_plugins()
        # WARNING: Slows down startup!!
        self.appsystem = AppSystem()
        # TODO: Fix this for updates-view handling
        self.show_all()

    def pick_resolution(self):
        """ Attempt to pick a good 16:9 resolution for the screen """
        scr = self.get_screen()
        w = scr.get_width()
        h = scr.get_height()

        res = self.resolutions
        res.reverse()
        for res_cand in res:
            if res_cand[0] > w or res_cand[1] > h:
                continue
            print(res_cand)
            self.set_size_request(res_cand[0], res_cand[1])
            return
        self.set_size_request(800, 600)

    def build_headerbar(self):
        """ Build main nav + search """
        self.hbar = Gtk.HeaderBar()
        self.hbar.set_show_close_button(True)
        self.set_titlebar(self.hbar)
        self.set_title("Software Center")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("system-software-install")

        self.search_button = Gtk.ToggleButton()
        img = Gtk.Image.new_from_icon_name(
            "edit-find-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        self.search_button.add(img)
        st = self.search_button.get_style_context()
        st.add_class("image-button")
        self.hbar.pack_end(self.search_button)

    def handle_key_event(self, w, e=None, d=None):
        """ Proxy window navigation events to the searchbar """
        return self.search_bar.handle_event(e)

    def build_search_bar(self):
        """ Build the actual search entry, hook it up """
        # Whack in a search box
        self.search_revealer = Gtk.Revealer.new()
        self.layout.pack_start(self.search_revealer, False, False, 0)
        self.search_bar = Gtk.SearchBar.new()
        self.search_revealer.add(self.search_bar)
        self.search_entry = Gtk.SearchEntry.new()
        self.search_entry.set_size_request(400, -1)

        search_layout = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.search_bar.add(search_layout)
        search_layout.pack_start(self.search_entry, True, True, 0)
        self.search_bar.connect_entry(self.search_entry)
        self.search_revealer.set_reveal_child(True)
        self.search_entry.set_hexpand(True)
        self.search_bar.set_show_close_button(True)
        self.connect('key-press-event', self.handle_key_event)

        self.search_button.bind_property('active', self.search_bar,
                                         'search-mode-enabled',
                                         GObject.BindingFlags.BIDIRECTIONAL)
        self.search_entry.connect('search-changed', self.search_changed)

    def add_item(self, id, item, popfilter):
        print("Search yield: {} - {}".format(id, item.get_name()))

    def clear(self):
        print("Not yet implemented: clear()")

    def search_changed(self, w, udata=None):
        """ Begin a search 1.2s after they stop typing as the built-in Gtk
            150ms is far too short for most normal human beings.
        """
        txt = self.search_entry.get_text().strip()
        if txt == "":
            return
        print("Search: {}".format(txt))

        if self.search_idle_timeout > 0:
            GLib.source_remove(self.search_idle_timeout)
        self.search_idle_timeout = GLib.timeout_add(1200, self.begin_search)

    def begin_search(self, udata=None):
        self.search_idle_timeout = 0

        txt = self.search_entry.get_text().strip()
        if txt == "":
            return False

        for plugin in self.plugins:
            plugin.populate_storage(self, PopulationFilter.SEARCH, txt)
        return False

    def init_plugins(self):
        """ Take care of setting up our plugins
            This takes special care to wrap the initial import in case we
            have a module level import that would fail, i.e. import of
            the snapd-glib binding
        """
        self.plugins = []
        snap = None
        osPlugin = None
        try:
            from xng.plugins.snapd import SnapdPlugin
            snap = SnapdPlugin()
        except Exception as e:
            print("snapd support unavailable on this system: {}".format(e))
            snap = None

        if snap is not None:
            self.plugins.append(snap)

        try:
            from xng.plugins.native import get_native_plugin
            osPlugin = get_native_plugin()
        except Exception as e:
            print("Native plugin support unavailable for this system: {}".
                  format(e))
        if osPlugin is not None:
            self.plugins.insert(0, osPlugin)
        else:
            print("WARNING: Unsupported OS, native packaging unavailable!")
