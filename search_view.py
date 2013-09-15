#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  search_view.py - SSC Search View
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
from gi.repository import Gtk, GObject

import pisi.api
from widgets import PackageLabel

class SearchView(Gtk.VBox):

    __gsignals__ = {
        'package-selected': (GObject.SIGNAL_RUN_FIRST, None,
                          (object,object))
    }
    
    def __init__(self, installdb, packagedb, basket):
        Gtk.VBox.__init__(self)

        self.installdb = installdb
        self.packagedb = packagedb
        self.basket = basket

        self.listbox_packages = Gtk.ListBox()

        # placeholder to show folks we're loading
        self.placeholder = Gtk.Label("<span font='30.5'>Searching..</span>")
        self.placeholder.set_use_markup(True)
        self.listbox_packages.set_placeholder(self.placeholder)
        self.placeholder.show_all()

        self.listbox_packages.connect("row-activated", self._selected)
        scroller = Gtk.ScrolledWindow(None, None)
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scroller.add(self.listbox_packages)
        
        center = Gtk.HBox()
        center.pack_start(scroller, True, True, 0)

        self.add(center)

    def search(self, name=None):
        GObject.idle_add(self._search, {'name' : name})

    def _search(self, terms=None):
        name = terms['name']
        lis = list()
        lis.append(name)
        packages = self.packagedb.search_package(lis)
        self.build_packages(packages)
        
    def _selected(self, box, row):
        if row is None:
            return
        child = row.get_children()[0]

        self.emit('package-selected', child.package, child.old_package)

    def do_reset(self):
        for child in self.listbox_packages.get_children():
            pan = child.get_children()[0]
            pkg = pan.package
            old_pkg = self.installdb.get_package(pkg.name) if self.installdb.has_package(pkg.name) else None
            pan.old_package = old_pkg
            pan.package = self.packagedb.get_package(pkg.name)
            pan.package_status = 'FORGET'
            pan.reset_image()
            while (Gtk.events_pending()):
                Gtk.main_iteration()

    def mark_selected(self, operation, package, old_package):
        for row in self.listbox_packages.get_children():
            child = row.get_children()[0]
            if child.package == package:
                child.mark_status(operation)

    def build_packages(self, packages):
        self.placeholder.set_markup("<span font='30.5'>Loading..</span>")
        for child in self.listbox_packages.get_children():
            child.destroy()

        appends = list()
        for pkg in packages:
            meta,pkg_ = pisi.api.info(pkg)
            package = meta.package
            old_package = self.installdb.get_package(pkg) if self.installdb.has_package(pkg) else None
            appends.append((package, old_package))
            while (Gtk.events_pending()):
                Gtk.main_iteration()

        appends.sort(key=lambda x: x[0].name)
        for new,old in appends:
            label = PackageLabel(new,old, True)
            label.sig_id = label.connect('operation-selected', self.op_select)
            status = self.basket.operation_for_package(new)
            label.mark_status(status)
            self.listbox_packages.add(label)
            self.listbox_packages.show_all()
            while (Gtk.events_pending()):
                Gtk.main_iteration()

    def op_select(self, package_label, operation, package, old_package):
        if operation == 'INSTALL':
            self.basket.install_package(package)
        elif operation == 'UNINSTALL':
            self.basket.remove_package(old_package)
        elif operation == 'UPDATE':
            self.basket.update_package(old_package, package)
        elif operation == 'FORGET':
            self.basket.forget_package(package)
        #self.mark_selected(operation, package, old_package)
