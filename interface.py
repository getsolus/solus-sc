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
from package_view import PackageView
from basket import BasketView


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
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        
        self.groups_page = GroupsView(self.groupdb)
        self.groups_page.connect('group-selected', self.group_selected)
        self.stack.add_named(self.groups_page, "groups")

        self.components_page = ComponentsView(self.componentdb, self.installdb)
        self.components_page.connect('package-selected', self.package_selected)
        self.stack.add_named(self.components_page, "components")

        self.package_page = PackageView(self.packagedb, self.installdb)
        self.package_page.connect('operation-selected', self.operation_selected)
        self.stack.add_named(self.package_page, "package")

        # Operations go in the basket
        self.basket = BasketView(self.packagedb, self.installdb)
        self.revealer = Gtk.Revealer()
        self.revealer.add(self.basket)
        
        # header area
        header = Gtk.Toolbar()
        header.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        box = Gtk.ButtonBox()
        box.set_layout(Gtk.ButtonBoxStyle.CENTER)
        box.get_style_context().add_class(Gtk.STYLE_CLASS_LINKED)
        box.get_style_context().add_class(Gtk.STYLE_CLASS_RAISED)

        self.back = Gtk.ToolButton("Back")
        self.back.set_icon_name("go-previous")
        self.back.connect("clicked", self.nav)
        header.add(self.back)

        soft = Gtk.ToggleButton("Software")
        box.add(soft)

        prefs = Gtk.ToggleButton("Preferences")
        box.add(prefs)

        updates = Gtk.ToggleButton("Updates")
        box.add(updates)

        item = Gtk.ToolItem()
        item.add(box)
        header.add(item)
        
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

        layout.pack_start(self.stack, True, True, 0)

        layout.pack_end(self.revealer, False, False, 0)

    def nav(self, btn):
        vis = self.stack.get_visible_child_name()
        if vis == "package":
            self.stack.set_visible_child_name('components')
        elif vis == "components":
            self.stack.set_visible_child_name("groups")
            self.back.set_sensitive(False)

    def group_selected(self, groups_view, group):
        comps = self.groupdb.get_group_components(group.name)
        self.components_page.set_from_components(comps)
        self.stack.set_visible_child_name('components')
        self.back.set_sensitive(True)

    def package_selected(self, package_view, package, old_package):
        self.package_page.set_from_package(package, old_package)
        op = self.basket.operation_for_package(package)
        if op is not None:
            self.package_page.mark_selection(op)
        self.stack.set_visible_child_name('package')
        self.back.set_sensitive(True)

    def operation_selected(self, view, operation, package, old_package):
        if operation == 'INSTALL':
            self.basket.install_package(package)
            view.mark_selection('INSTALL')
        elif operation == 'UNINSTALL':
            self.basket.remove_package(old_package)
            view.mark_selection('UNINSTALL')
        elif operation == 'UPDATE':
            self.basket.update_package(old_package, new_package)
            view.mark_selection('UPDATE')
        elif operation == 'FORGET':
            self.basket.forget_package(package)
            view.mark_selection(None)

        if self.basket.operation_count() >= 1:
            self.revealer.set_reveal_child(True)
        else:
            self.revealer.set_reveal_child(False)
