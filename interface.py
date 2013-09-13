#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  interface.py - SSC Main Window
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
from gi.repository import Gtk
import pisi.db.componentdb as componentdb
import pisi.db.installdb as installdb
import pisi.db.packagedb as packagedb
import pisi.db.groupdb as groupdb
import pisi.api

from groups import GroupsView


class PackagePanel(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.label_name = Gtk.Label("")
        self.desc = Gtk.Label("")
        
        self.pack_start(self.label_name, False, False, 0)
        self.pack_start(self.desc, True, True, 0)

    def set_from_package(self, package):
        self.label_name.set_label(package.name)
        self.desc.set_markup(str(package.description))


class SSCWindow(Gtk.Window):
    
    def __init__(self):
        Gtk.Window.__init__(self)
        
        self.set_title("Software")
        self.connect("destroy", Gtk.main_quit)
        self.set_size_request(700, 500)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.groups = groupdb.GroupDB()
        self.stack = Gtk.Stack()
        self.groups_page = GroupsView(self.groups)
        self.stack.add_named(self.groups_page, "groups")
        
        # header area
        header = Gtk.Toolbar()
        header.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        # butt it all up to the end of the toolbar now
        sep = Gtk.SeparatorToolItem()
        sep.set_expand(True)
        sep.set_draw(False)
        header.add(sep)

        # search
        search = Gtk.ToolItem()
        search_entry = Gtk.Entry()
        search_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "edit-find-symbolic")
        search.add(search_entry)
        search.set_margin_right(3)
        header.add(search)
        layout = Gtk.VBox()
        layout.pack_start(header, False, False, 0)
        self.add(layout)

        self.componentdb = componentdb.ComponentDB()
        self.installdb = installdb.InstallDB()
        self.packagedb = packagedb.PackageDB()
        
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

        self.treeview_packages = Gtk.TreeView()
        selection = self.treeview_packages.get_selection()
        selection.connect("changed", self.open_package)
        
        ren = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Package", ren)
        column.add_attribute(ren, "markup", 0)
        self.treeview_packages.append_column(column)
        
        ren = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Installed Version", ren)
        column.add_attribute(ren, "markup", 1)
        self.treeview_packages.append_column(column)

        ren = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Available Version", ren)
        column.add_attribute(ren, "markup", 2)
        self.treeview_packages.append_column(column)

        scroller2 = Gtk.ScrolledWindow(None, None)
        scroller2.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller2.add(self.treeview_packages)
        
        center = Gtk.HBox()
        center.pack_start(scroller, False, False, 0)
        center.pack_start(scroller2, True, True, 0)
        #layout.pack_start(center, True, True, 0)

        layout.pack_start(self.stack, True, True, 0)
        self.build_components()

        # Package panel
        self.package_panel = PackagePanel()
        self.package_revealer = Gtk.Revealer()
        self.package_revealer.add(self.package_panel)
        layout.pack_end(self.package_revealer, False, False, 0)

    def open_package(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is None:
            self.package_revealer.set_reveal_child(False)
            return
        row = model[treeiter]
        package = row[3]

        self.package_panel.set_from_package(package)
        self.package_revealer.set_reveal_child(True)

    def open_component(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is None:
            return
        row = model[treeiter]
        component = row[2]

        self.build_packages(component)

    def build_packages(self, component=None):
        pkgs = component.packages
        model = Gtk.ListStore(str,str,str,object,object)
        for pkg in component.packages:
            meta,pkg_ = pisi.api.info(pkg)
            package = meta.package
            n_vers = package.version
            if self.installdb.has_package(pkg):
                i_pkg = self.installdb.get_package(pkg)
                model.append(["<big>%s</big>\n<small>%s</small>" % (package.name, package.summary), i_pkg.version, n_vers, package, i_pkg])
            else:
                model.append(["<big>%s</big>\n<small>%s</small>" % (package.name, package.summary), None, n_vers, package, None])
        model.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.treeview_packages.set_model(model)

    def build_components(self):
        store = Gtk.ListStore(str,str,object)
        for component_key in self.componentdb.list_components():
            component = self.componentdb.get_component(component_key)
            store.append([str(component.localName), str(component.description), component])
        store.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.components_view.set_model(store)
        
