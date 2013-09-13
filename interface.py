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
from components import ComponentsView

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

        self.groupdb = groupdb.GroupDB()
        self.componentdb = componentdb.ComponentDB()
        self.installdb = installdb.InstallDB()
        self.packagedb = packagedb.PackageDB()
        
        self.stack = Gtk.Stack()
        
        self.groups_page = GroupsView(self.groupdb)
        self.groups_page.connect('group-selected', self.group_selected)
        self.stack.add_named(self.groups_page, "groups")

        self.components_page = ComponentsView(self.componentdb, self.installdb)
        self.stack.add_named(self.components_page, "components")
        
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

        #layout.pack_start(center, True, True, 0)

        layout.pack_start(self.stack, True, True, 0)

        # Package panel
        self.package_panel = PackagePanel()
        self.package_revealer = Gtk.Revealer()
        self.package_revealer.add(self.package_panel)
        layout.pack_end(self.package_revealer, False, False, 0)

    def group_selected(self, groups_view, group):
        comps = self.groupdb.get_group_components(group.name)
        self.components_page.set_from_components(comps)
        self.stack.set_visible_child_name('components')

    def open_package(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is None:
            self.package_revealer.set_reveal_child(False)
            return
        row = model[treeiter]
        package = row[3]

        self.package_panel.set_from_package(package)
        self.package_revealer.set_reveal_child(True)
