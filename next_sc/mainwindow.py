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
from plugins.native import get_native_plugin
from plugins.snapd import SnapdPlugin
from plugins.base import PopulationFilter
from . import models
import traceback
import sys


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
            traceback.print_exc()
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
        """ TODO: Not use hardcoded demos! """
        # Main treeview where it's all happening. Single click activate
        self.tview = Gtk.TreeView()
        self.tview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.tview.set_activate_on_single_click(True)

        self.scroll = Gtk.ScrolledWindow.new(None, None)
        self.add(self.scroll)

        # Defugly
        self.tview.set_property("enable-grid-lines", False)
        self.tview.set_property("headers-visible", False)
        self.scroll.add(self.tview)

        # Icon for testing UI layout
        ren = Gtk.CellRendererPixbuf()
        ren.set_property("stock-size", Gtk.IconSize.DIALOG)
        ren.set_padding(5, 5)
        column = Gtk.TreeViewColumn("Icon", ren, icon_name=1)
        self.tview.append_column(column)
        ren.set_property("xalign", 0.0)

        # Set up display columns
        ren = Gtk.CellRendererText()
        ren.set_padding(5, 5)
        column = Gtk.TreeViewColumn("Name", ren, markup=0)
        self.tview.append_column(column)
        self.tview.set_search_column(1)

        self.show_all()

        store = models.ListingModel()
        self.tview.set_model(store)

        # Pump stuff into it!
        for p in self.plugins:
            p.populate_storage(store, PopulationFilter.INSTALLED, None)
