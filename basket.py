#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  basket.py - SSC Package Basket
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


class BasketView(Gtk.VBox):
    
    def __init__(self, packagedb, installdb):
        Gtk.VBox.__init__(self)

        self.title = Gtk.Label("Software basket")
        self.title.set_use_markup(True)

        toolbar = Gtk.Toolbar()
        toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        label_item = Gtk.ToolItem()
        label_item.add(self.title)
        toolbar.add(label_item)

        self.pack_start(toolbar, False, False, 0)

        sep = Gtk.SeparatorToolItem()
        sep.set_expand(True)
        sep.set_draw(False)
        toolbar.add(sep)
        
        self.apply = Gtk.ToolButton("Apply")
        self.apply.set_label("Apply")
        self.apply.set_is_important(True)
        self.apply.set_icon_name("emblem-ok-symbolic")
        toolbar.add(self.apply)
        self.operations = dict()

        self.update_ui()

    def update_ui(self):
        count = self.operation_count()
        if count == 0:
            self.title.set_markup("No operations are currently pending")
            self.apply.set_sensitive(False)
            return
        self.apply.set_sensitive(True)
        if count > 1:
            self.title.set_markup("%d operations pending" % self.operation_count())
        else:
            self.title.set_markup("One operation pending")

    def operation_for_package(self, package):
        if package.name in self.operations:
            return self.operations[package.name]
        return None

    def operation_count(self):
        return len(self.operations)

    def forget_package(self, package):
        if package.name in self.operations:
            self.operations.pop(package.name, None)
        self.update_ui()

    def remove_package(self, old_package):
        self.operations[old_package.name] = 'UNINSTALL'
        self.update_ui()

    def install_package(self, new_package):
        self.operations[new_package.name] = 'INSTALL'
        self.update_ui()

    def update_package(self, old_package, new_package):
        self.operations[old_package.name] = 'UPDATE'
        self.update_ui()
