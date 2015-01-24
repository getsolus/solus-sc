#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  components.py - SSC Component Navigation
#  
#  Copyright 2014 Ikey Doherty <ikey.doherty@gmail.com>
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

class ComponentsView(Gtk.VBox):

    __gsignals__ = {
        'package-selected': (GObject.SIGNAL_RUN_FIRST, None,
                          (object,object))
    }
    
    def __init__(self, components, installdb, basket):
        Gtk.VBox.__init__(self)

        self.componentdb = components
        self.installdb = installdb
        self.basket = basket
        
        self.components_view = Gtk.TreeView()
        self.components_view.set_grid_lines(Gtk.TreeViewGridLines.HORIZONTAL)
        self.components_view.set_size_request(10, 10)
        self.components_view.set_headers_visible(False)
        selection = self.components_view.get_selection()
        self._sig_id = selection.connect("changed", self.open_component)
        ren = Gtk.CellRendererText()
        ren.set_property("ypad", 8)
        column = Gtk.TreeViewColumn("Component", ren)
        column.add_attribute(ren, "markup", 0)
        self.components_view.append_column(column)

        scroller = Gtk.ScrolledWindow(None, None)
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.add_with_viewport(self.components_view)

        self.listbox_packages = Gtk.ListBox()

        # placeholder to show folks we're loading
        self.placeholder = Gtk.Label("<span font='30.5'>Loading..</span>")
        self.placeholder.set_use_markup(True)
        #self.listbox_packages.set_placeholder(self.placeholder)
        self.placeholder.show_all()

        self.listbox_packages.connect("row-activated", self._selected)
        scroller2 = Gtk.ScrolledWindow(None, None)
        scroller2.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller2.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scroller2.add(self.listbox_packages)
        
        center = Gtk.HBox()
        center.pack_start(scroller, False, False, 0)
        center.pack_start(scroller2, True, True, 0)

        self.pack_start(center, True, True, 0)

    def _selected(self, box, row):
        if row is None:
            return
        child = row.get_children()[0]

        self.emit('package-selected', child.package, child.old_package)
        
    def set_from_components(self, components):
        store = Gtk.ListStore(str,str,object)
        for component_key in components:
            component = self.componentdb.get_component(component_key)
            store.append([str(component.localName), str(component.localName), component])
        store.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.components_view.set_model(store)

        component = store[0][2]

        self.components_view.get_selection().handler_block(self._sig_id)
        self.components_view.set_cursor(0)
        self.components_view.get_selection().handler_unblock(self._sig_id)
        self.build_packages(component)
        
        self.show_all()

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

    def open_component(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is None:
            return
        row = model[treeiter]
        component = row[2]

        self.components_view.set_sensitive(False)
        GObject.idle_add(self.build_packages, component)

    def mark_selected(self, operation, package, old_package):
        for row in self.listbox_packages.get_children():
            child = row.get_children()[0]
            if child.package == package:
                child.mark_status(operation)

    def build_packages(self, component=None):
        self.placeholder.set_markup("<span font='30.5'>Loading..</span>")
        for child in self.listbox_packages.get_children():
            child.destroy()

        pkgs = component.packages
        appends = list()
        if len(pkgs) == 0:
            self.placeholder.set_markup("<big>No packages matched your query</big>")
            self.components_view.set_sensitive(True)
            return
        for pkg in component.packages:
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
        self.components_view.set_sensitive(True)

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
