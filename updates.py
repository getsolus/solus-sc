#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  updates.py - SSC Update Viewer
#  
#  Copyright 2013 Ikey Doherty <ikey@solusos.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
# 
import gi.repository
from gi.repository import Gtk, GObject, Gdk

import pisi.api
import comar
import threading

from widgets import PackageLabel

class UpdatesView(Gtk.VBox):

    def __init__(self, packagedb, installdb):
        Gtk.VBox.__init__(self)

        self.packagedb = packagedb
        self.installdb = installdb
        
        self.updates_list = Gtk.ListBox()
                
        scroller = Gtk.ScrolledWindow(None, None)
        scroller.add(self.updates_list)
        self.placeholder = Gtk.Label("")
        self.placeholder.set_markup("<big>No updates are available at this time</big>")

        self.placeholder_box = Gtk.HBox()
        self.placeholder_box.add(self.placeholder)

        # Check again for updates
        check_updates = Gtk.Button("Check for updates now")
        self.placeholder_box.pack_end(check_updates, False, False, 0)
        check_updates.connect("clicked", self.refresh_repos)
        
        self.placeholder_box.set_border_width(50)
        self.placeholder_box.show_all()

        self.updates_list.set_placeholder(self.placeholder_box)

        self.pack_start(scroller, True, True, 0)

        #self.refresh_repos(self)

    def refresh_repos(self, btn=None):
        th = threading.Thread(target=self._refresh_repos)
        th.start()

    def _refresh_repos(self):
        link = comar.Link()
        pmanager = link.System.Manager["pisi"]
        pmanager.updateAllRepositories()
        Gdk.threads_enter()
        self._load_updates()
        Gdk.threads_leave()

    def load_updates(self):
        GObject.idle_add(self._load_updates)

    def _load_updates(self):
        updates = pisi.api.list_upgradable()
        for update in updates:
            old_pkg = self.installdb.get_package(update)
            new_pkg = self.packagedb.get_package(update)

            panel = PackageLabel(new_pkg, old_pkg, interactive=True)
            panel.mark_status(None)
            self.updates_list.add(panel)
            while (Gtk.events_pending()):
                Gtk.main_iteration()

            panel.show_all()
