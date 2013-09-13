#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  components.py - SSC Component Navigation
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

GENERIC = "package-x-generic"

def do_justif(label):
    label.set_alignment(0.0, 0.5)
    label.set_justify(Gtk.Justification.LEFT)

class PackageLabel(Gtk.VBox):

    def __init__(self, pkg, old_pkg):
        Gtk.VBox.__init__(self)

        self.set_border_width(4)
        self.header = Gtk.HBox()
        self.image = Gtk.Image()
        if pkg.icon is not None:
            self.image.set_from_icon_name(pkg.icon, Gtk.IconSize.DIALOG)
        else:
            self.image.set_from_icon_name(GENERIC, Gtk.IconSize.DIALOG)

        self.header.pack_start(self.image, False, False, 5)
        self.label_title = Gtk.Label("<b>%s</b> - <small>%s</small>\n%s" % (pkg.name, pkg.version, str(pkg.summary)))
        self.label_title.set_use_markup(True)
        do_justif(self.label_title)
        self.label_title.set_line_wrap(True)
        self.header.pack_start(self.label_title, False, False, 0)


        image_status = Gtk.Image()
        if old_pkg is not None:
            new_version = pkg.release
            old_version = old_pkg.release

            if new_version > old_version:
                image_status.set_from_icon_name("package-installed-outdated", Gtk.IconSize.SMALL_TOOLBAR)
            else:
                image_status.set_from_icon_name("package-installed-updated", Gtk.IconSize.SMALL_TOOLBAR)
        else:
            image_status.set_from_icon_name("package-available", Gtk.IconSize.SMALL_TOOLBAR)
        self.header.pack_end(image_status, False, False, 0)
        
        self.package = pkg
        self.old_package = old_pkg
        
        self.pack_start(self.header, True, True, 0)

class ComponentsView(Gtk.VBox):

    __gsignals__ = {
        'package-selected': (GObject.SIGNAL_RUN_FIRST, None,
                          (object,object))
    }
    
    def __init__(self, components, installdb):
        Gtk.VBox.__init__(self)

        self.componentdb = components
        self.installdb = installdb
        
        self.components_view = Gtk.TreeView()
        self.components_view.set_headers_visible(False)
        selection = self.components_view.get_selection()
        selection.connect("changed", self.open_component)
        ren = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Component", ren)
        column.add_attribute(ren, "markup", 0)
        self.components_view.append_column(column)

        scroller = Gtk.ScrolledWindow(None, None)
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.add(self.components_view)

        self.listbox_packages = Gtk.ListBox()
        self.listbox_packages.connect("row-selected", self._selected)
        scroller2 = Gtk.ScrolledWindow(None, None)
        scroller2.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller2.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scroller2.add(self.listbox_packages)
        
        center = Gtk.HBox()
        center.pack_start(scroller, False, False, 0)
        center.pack_start(scroller2, True, True, 0)

        self.add(center)

    def _selected(self, box, row):
        if row is None:
            return
        child = row.get_children()[0]

        self.emit('package-selected', child.package, child.old_package)
        
    def set_from_components(self, components):
        store = Gtk.ListStore(str,str,object)
        for component_key in components:
            component = self.componentdb.get_component(component_key)
            store.append([str(component.localName), str(component.description), component])
        store.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.components_view.set_model(store)

        component = store[0][2]
        self.build_packages(component)
        self.show_all()

    def open_component(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is None:
            return
        row = model[treeiter]
        component = row[2]

        GObject.idle_add(self.build_packages, component)

    def build_packages(self, component=None):
        for child in self.listbox_packages.get_children():
            self.listbox_packages.remove(child)
            while (Gtk.events_pending()):
                Gtk.main_iteration()

        pkgs = component.packages
        appends = list()
        for pkg in component.packages:
            meta,pkg_ = pisi.api.info(pkg)
            package = meta.package
            old_package = self.installdb.get_package(pkg) if self.installdb.has_package(pkg) else None
            appends.append((package, old_package))
            while (Gtk.events_pending()):
                Gtk.main_iteration()

        appends.sort(key=lambda x: x[0].name)
        for new,old in appends:
            label = PackageLabel(new,old)
            self.listbox_packages.add(label)
            self.listbox_packages.show_all()
            while (Gtk.events_pending()):
                Gtk.main_iteration()
