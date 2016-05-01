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
from pisi.db.installdb import InstallDB


class ScPackageView(Gtk.VBox):

    installdb = None
    scroll = None
    tview = None

    def __init__(self):
        Gtk.VBox.__init__(self, 0)
        # This stuff needs asyncing!
        self.installdb = InstallDB()

        self.scroll = Gtk.ScrolledWindow(None, None)
        self.pack_start(self.scroll, True, True, 0)

        self.tview = Gtk.TreeView()
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

        GLib.idle_add(self.init_view)

    def init_view(self):
        model = Gtk.ListStore(str, str, str)
        model.set_sort_column_id(1, Gtk.SortType.ASCENDING)
        for pkg_name in self.installdb.list_installed():
            pkg = self.installdb.get_package(pkg_name)

            p_print = "<b>%s</b> - %s\n%s" % (str(pkg.name), str(pkg.version),
                                              str(pkg.summary))

            icon = "package-x-generic"
            if pkg.icon is not None:
                icon = str(pkg.icon)

            model.append([p_print, pkg_name, icon])

            while (Gtk.events_pending()):
                Gtk.main_iteration()
        self.tview.set_model(model)
        return False
