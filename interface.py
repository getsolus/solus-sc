#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  interface.py - SSC Main Window
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
import sys

from gi.repository import Gtk, GObject
import pisi.db
import pisi.db.componentdb as componentdb
import pisi.db.installdb as installdb
import pisi.db.packagedb as packagedb
import pisi.db.groupdb as groupdb
import pisi.api

from groups import GroupsView
from components import ComponentsView
from package_view import PackageView
from basket import BasketView
from updates import UpdatesView

class SSCWindow(Gtk.Window):
    
    def __init__(self):
        Gtk.Window.__init__(self)
        
        self.set_wmclass("Software", "Software")
        self.set_title("Software")
        self.connect("destroy", Gtk.main_quit)
        self.set_size_request(700, 500)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.groupdb = groupdb.GroupDB()
        self.componentdb = componentdb.ComponentDB()
        self.installdb = installdb.InstallDB()
        self.packagedb = packagedb.PackageDB()

        # Operations go in the basket
        self.basket = BasketView(self.packagedb, self.installdb)
        self.basket.connect('basket-changed', self.do_reset)
                
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        
        self.groups_page = GroupsView(self.groupdb, self.packagedb, self.installdb, self.basket)
        self.groups_page.connect('group-selected', self.group_selected)
        self.stack.add_named(self.groups_page, "groups")

        self.components_page = ComponentsView(self.componentdb, self.installdb, self.basket)
        self.components_page.connect('package-selected', self.package_selected)
        self.stack.add_named(self.components_page, "components")

        self.package_page = PackageView(self.packagedb, self.installdb)
        self.package_page.connect('operation-selected', self.operation_selected)
        self.stack.add_named(self.package_page, "package")
        
        # header area
        header = Gtk.Toolbar()
        header.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        box = Gtk.ButtonBox()
        box.set_layout(Gtk.ButtonBoxStyle.CENTER)
        box.get_style_context().add_class(Gtk.STYLE_CLASS_LINKED)
        box.get_style_context().add_class(Gtk.STYLE_CLASS_RAISED)

        self.buttons = dict()
        soft = Gtk.ToggleButton("Software")
        self.buttons[soft] = "software"
        soft.sig_id = soft.connect("clicked", self.main_header_nav, "software")
        box.add(soft)

        prefs = Gtk.ToggleButton("Preferences")
        prefs.sig_id = prefs.connect("clicked", self.main_header_nav, "preferences")
        self.buttons[prefs] = "preferences"
        box.add(prefs)

        self.update = Gtk.ToggleButton("Updates")
        self.update.sig_id = self.update.connect("clicked", self.main_header_nav, "updates")
        self.buttons[self.update] = "updates"
        box.add(self.update)

        layout = Gtk.VBox()
        self.add(layout)

        self.stack_main = Gtk.Stack()
        self.stack_main.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        self.updates_view = UpdatesView(self.packagedb, self.installdb, self.basket)
        self.stack_main.add_named(self.stack, "software")
        self.stack_main.add_named(self.updates_view, "updates")
        
        layout.pack_start(self.stack_main, True, True, 0)        
        layout.pack_end(self.basket, False, False, 0)

        self.back = Gtk.Button()
        itheme = Gtk.IconTheme.get_default()
        ic = itheme.load_icon("go-previous-symbolic", 16, Gtk.IconLookupFlags.GENERIC_FALLBACK)
        im = Gtk.Image()
        im.set_from_pixbuf(ic)
        self.back.set_image(im)
        self.back.connect('clicked', self.nav)
        self.back.set_sensitive(False)

        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.show_all()
        header.pack_start(self.back)
        
        header.set_custom_title(box)
        self.set_titlebar(header)

        self.show_all()
        self.stack_main.hide()
        GObject.idle_add(self.update_count)

        if "--update" in sys.argv:
            self.select_main_page("updates")
        else:
            self.select_main_page("software")

    def do_reset(self, basket, extra=None):
        pisi.db.invalidate_caches()
        self.groupdb = groupdb.GroupDB()
        self.componentdb = componentdb.ComponentDB()
        self.installdb = installdb.InstallDB()
        self.packagedb = packagedb.PackageDB()

        for page in [self.components_page, self.package_page, self.groups_page, self.updates_view]:
            page.groupdb = self.groupdb
            page.componentdb = self.componentdb
            page.installdb = self.installdb
            page.packagedb = self.packagedb

            if hasattr(page, 'do_reset'):
                page.do_reset()
                
        # reset update count
        self.update_count()

    def update_count(self):
        count = len(pisi.api.list_upgradable())
        if count > 0:
            self.update.set_label("Updates (%d)" % count)
        else:
            self.update.set_label("Updates")

    def main_header_nav(self, btn, data=None):
        self.select_main_page(data)

    def select_main_page(self, name):
        buttons_disable = [btn for btn in self.buttons if self.buttons[btn] != name]
        button_enable = [btn for btn in self.buttons if self.buttons[btn] == name][0]

        button_enable.handler_block(button_enable.sig_id)
        button_enable.set_active(True)
        button_enable.handler_unblock(button_enable.sig_id)
        
        for button in buttons_disable:
            button.handler_block(button.sig_id)
            button.set_active(False)
            button.handler_unblock(button.sig_id)
        self.stack_main.set_visible_child_name(name)
        self.stack_main.show_all()


    def nav(self, btn):
        vis = self.stack.get_visible_child_name()
        if vis == "package":
            self.stack.set_visible_child_name('components')
        elif vis == "components":
            self.stack.set_visible_child_name("groups")
            self.back.set_sensitive(False)

    def group_selected(self, groups_view, group):
        # Do not lock up for anyone :)
        self.stack.set_visible_child_name('components')
        self.back.set_sensitive(True)
        GObject.idle_add(self._group_selected, group)

    def _group_selected(self, group):
        comps = self.groupdb.get_group_components(group.name)
        self.components_page.set_from_components(comps)

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
            self.basket.update_package(old_package, package)
            view.mark_selection('UPDATE')
        elif operation == 'FORGET':
            self.basket.forget_package(package)
            view.mark_selection(None)
        self.components_page.mark_selected(operation, package, old_package)
