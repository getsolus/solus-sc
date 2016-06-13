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

from gi.repository import Gtk, GLib, GdkPixbuf


class ScPackageView(Gtk.VBox):

    scroll = None
    tview = None
    appsystem = None
    basket = None

    def __init__(self, basket, appsystem):
        Gtk.VBox.__init__(self, 0)
        self.basket = basket
        self.appsystem = appsystem

        self.scroll = Gtk.ScrolledWindow(None, None)
        self.scroll.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.scroll.set_overlay_scrolling(False)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_property("kinetic-scrolling", True)
        self.pack_start(self.scroll, True, True, 0)

        self.tview = Gtk.TreeView()
        self.tview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        # Defugly
        self.tview.set_property("enable-grid-lines", False)
        self.tview.set_property("headers-visible", False)
        self.scroll.add(self.tview)

        # img view
        ren = Gtk.CellRendererPixbuf()
        ren.set_property("stock-size", Gtk.IconSize.DIALOG)
        ren.set_padding(5, 2)
        column = Gtk.TreeViewColumn("Icon", ren, icon_name=2)
        self.tview.append_column(column)

        # Set up display columns
        ren = Gtk.CellRendererText()
        ren.set_padding(5, 5)
        column = Gtk.TreeViewColumn("Name", ren, markup=0)
        self.tview.append_column(column)
        self.tview.set_search_column(1)

        # Details
        ren = Gtk.CellRendererPixbuf()
        ren.set_padding(5, 5)
        column = Gtk.TreeViewColumn("Details", ren, icon_name=3)
        self.tview.append_column(column)
        ren.set_property("xalign", 1.0)

    def init_view(self):
        model = Gtk.ListStore(str, str, str, str)
        model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
        for pkg_name in self.basket.installdb.list_installed():
            pkg = self.basket.installdb.get_package(pkg_name)

            summary = self.appsystem.get_summary(pkg)
            summary = str(summary)
            if len(summary) > 76:
                summary = "%s…" % summary[0:76]

            summary = GLib.markup_escape_text(summary)

            name = str(pkg.name)
            p_print = "<b>%s</b> - %s\n%s" % (name, str(pkg.version),
                                              summary)
            icon = "package-x-generic"
            if pkg.icon is not None:
                icon = str(pkg.icon)

            model.append([p_print, pkg_name, icon, "go-next-symbolic"])

        self.tview.set_model(model)
        return False
