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

from gi.repository import Gtk, GLib
from plugins.base import PopulationFilter
from . import models

        
class AvailableView(Gtk.Box):

    # Our next_sc plugin set
    plugins = None

    # Our appsystem for resolving metadata
    appsystem = None

    groups_view = None

    def __init__(self, appsystem, plugins, groups_view):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.appsystem = appsystem
        self.plugins = plugins
        self.groups_view = groups_view

        # Main treeview where it's all happening. Single click activate
        self.tview = Gtk.TreeView()
        self.tview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.tview.set_activate_on_single_click(True)
        self.tview.connect_after('row-activated', self.on_row_activated)

        self.scroll = Gtk.ScrolledWindow.new(None, None)
        self.pack_start(self.scroll, True, True, 0)

        # Defugly
        self.tview.set_property("enable-grid-lines", False)
        self.tview.set_property("headers-visible", False)
        self.scroll.add(self.tview)

        # Icon for testing UI layout
        ren = Gtk.CellRendererPixbuf()
        ren.set_property("stock-size", Gtk.IconSize.DIALOG)
        ren.set_padding(5, 5)
        column = Gtk.TreeViewColumn("Icon", ren, pixbuf=1)
        self.tview.append_column(column)
        ren.set_property("xalign", 0.0)

        # Set up display columns
        ren = Gtk.CellRendererText()
        ren.set_padding(5, 5)
        column = Gtk.TreeViewColumn("Name", ren, markup=0)
        self.tview.append_column(column)
        self.tview.set_search_column(1)

        self.show_all()

    def set_category(self, c):
        store = models.ListingModel(self.appsystem)
        self.tview.set_model(store)

        # Pump stuff into it!
        for p in self.plugins:
            p.populate_storage(store, PopulationFilter.CATEGORY, c)

    def on_row_activated(self, tview, path, column, udata=None):
        """ User clicked a row, now try to load the page """
        model = tview.get_model()
        row = model[path]

        pkg_object = row[3]
        self.groups_view.select_details(pkg_object)
