#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  groups.py - SSC Group Navigation
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

class GroupsView(Gtk.VBox):

    __gsignals__ = {
        'group-selected': (GObject.SIGNAL_RUN_FIRST, None,
                          (object,))
    }
    
    def __init__(self, groups, packagedb, installdb, basket):
        Gtk.VBox.__init__(self)

        self.packagedb = packagedb
        self.installdb = installdb
        self.basket = basket
        
        self.grid = Gtk.Grid()
        self.grid.set_margin_top(20)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
        self.stack.add_named(self.grid, "groups")

        self.packages_list = Gtk.ListBox()
        self.scroller = Gtk.ScrolledWindow(None, None)
        self.scroller.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.scroller.add(self.packages_list)
        self.stack.add_named(self.scroller, "packages")

        self.pack_start(self.stack, True, True, 0)
        
        ## Grid logic
        row = 0
        column = 0

        self.groups = groups
        group_names = self.groups.list_groups()
        max_columns = int(len(group_names) / 2)

        self.grid.set_border_width(40)
        row = 1
        column = 0
        
        row += 1
        
        for group_name in self.groups.list_groups():
            if column >= max_columns:
                column = 1
                row += 1
            else:
                column += 1
            group = self.groups.get_group(group_name)

            btn = Gtk.Button()
            btn.set_relief(Gtk.ReliefStyle.NONE)
            components = self.groups.get_group_components(group_name)
            label = Gtk.Label("<b>%s</b>\n<small>%d categories</small>" % (str(group.localName), len(components)))
            label.set_use_markup(True)
            label.set_justify(Gtk.Justification.LEFT)
            label.set_alignment(0.1, 0.1)
            image = Gtk.Image()
            image.set_from_icon_name(group.icon, Gtk.IconSize.DIALOG)

            btn_layout = Gtk.HBox()
            btn.add(btn_layout)
            btn_layout.pack_start(image, False, False, 5)
            btn_layout.pack_start(label, True, True, 0)

            btn.key_word = group
            btn.connect("clicked", lambda x: self.emit('group-selected', x.key_word))
            self.grid.attach(btn, column-1, row, 1, 1)

        self.packages = list()
        self.do_reset()

        self.packages_list.set_sort_func(self.sort, None)

    def searching(self, entry, event=None):
        text = entry.get_text().strip()
        if text == "":
            self.stack.set_visible_child_name("groups")
        else:
            self.stack.set_visible_child_name("packages")
            self.packages_list.set_filter_func(self.filter, text)

    def filter(self, row, text):
        child = row.get_children()[0]
        package = child.package
        
        if text in package.name or text in str(package.summary).lower():
            return True
        return False
        
    def sort(self, row1, row2, data=None):
        package1 = row1.get_children()[0].package
        package2 = row2.get_children()[0].package

        return cmp(package1.name, package2.name)
        
    def rebuild_all_packages(self, data=None):
        for child in self.packages_list.get_children():
            child.destroy()
            
        for pkg in pisi.api.list_available():
            package = self.packagedb.get_package(pkg)
            old_package = self.installdb.get_package(pkg) if self.installdb.has_package(pkg) else None

            status = self.basket.operation_for_package(package)
            panel = PackageLabel(package, old_package, interactive=True)
            panel.sig_id = panel.connect('operation-selected', self.op_select)
            panel.mark_status(status)
            self.packages_list.add(panel)
            self.packages_list.show_all()
            while (Gtk.events_pending()):
                Gtk.main_iteration()
        print "Done"

    def op_select(self, package_label, operation, package, old_package):
        if operation == 'INSTALL':
            self.basket.install_package(package)
        elif operation == 'UNINSTALL':
            self.basket.remove_package(old_package)
        elif operation == 'UPDATE':
            self.basket.update_package(old_package, package)
        elif operation == 'FORGET':
            self.basket.forget_package(package)
            
    def do_reset(self):
        GObject.idle_add(self.rebuild_all_packages)
