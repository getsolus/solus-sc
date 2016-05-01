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

from gi.repository import Gtk, GLib
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
        self.scroll.add(self.tview)

        # Set up display columns
        ren = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Name", ren, text=0)
        self.tview.append_column(column)

        # version
        ren = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Version", ren, text=1)
        self.tview.append_column(column)

        # summary
        ren = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Summary", ren, text=2)
        self.tview.append_column(column)

        GLib.idle_add(self.init_view)

    def init_view(self):
        model = Gtk.ListStore(str, str, str)
        for pkg_name in self.installdb.list_installed():
            pkg = self.installdb.get_package(pkg_name)
            model.append([str(pkg.name), str(pkg.version), str(pkg.summary)])

            while (Gtk.events_pending()):
                Gtk.main_iteration()
        self.tview.set_model(model)
        return False
