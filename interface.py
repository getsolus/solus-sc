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

from gi.repository import Gtk, GObject, Gio
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
    
    old_view = ''

    def __init__(self):
        Gtk.Window.__init__(self)
        
        self.init_css()
        self.set_title("Software")
        self.connect("destroy", Gtk.main_quit)
        self.set_default_size(700, 500)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.groupdb = groupdb.GroupDB()
        self.componentdb = componentdb.ComponentDB()
        self.installdb = installdb.InstallDB()
        self.packagedb = packagedb.PackageDB()

        # Operations go in the basket
        self.basket = BasketView(self.packagedb, self.installdb)
        self.basket.connect('basket-changed', self.do_reset)
        self.basket.connect('apply', self.do_apply)
                
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        
        self.groups_page = GroupsView(self.groupdb, self.packagedb, self.installdb, self.basket)
        self.groups_page.connect('group-selected', self.group_selected)
        self.groups_page.connect('package-selected', self.package_selected)
        self.stack.add_named(self.groups_page, "groups")

        self.components_page = ComponentsView(self.componentdb, self.installdb, self.basket)
        self.components_page.connect('package-selected', self.package_selected)
        self.stack.add_named(self.components_page, "components")

        self.package_page = PackageView(self.packagedb, self.installdb)
        self.package_page.connect('operation-selected', self.operation_selected)
        self.stack.add_named(self.package_page, "package")

        layout = Gtk.VBox()
        self.add(layout)

        self.search_bar = Gtk.SearchBar()
        self.search_bar.get_style_context().add_class("primary-toolbar")
        self.search_bar.set_halign(Gtk.Align.FILL)

        entry = Gtk.SearchEntry()
        entry.connect("search-changed", self.search_changed)
        self.search_bar.add(entry)
        self.search_bar.connect_entry(entry)
        layout.pack_start(self.search_bar, False, False, 0)
        self.search_entry = entry

        self.connect("key-press-event", lambda x,y: self.search_bar.handle_event(y))

        self.stack_main = Gtk.Stack()
        self.stack_main.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        self.updates_view = UpdatesView(self.packagedb, self.installdb, self.basket)
        self.stack_main.add_named(self.stack, "software")
        self.stack_main.child_set_property(self.stack, "title", "Software")
        self.stack_main.add_named(self.updates_view, "updates")
        self.stack_main.child_set_property(self.updates_view, "title", "Updates")
        
        layout.pack_start(self.stack_main, True, True, 0)        
        layout.pack_end(self.basket, False, False, 0)

        self.back = Gtk.Button.new_from_icon_name("go-previous-symbolic", Gtk.IconSize.BUTTON)
        self.back.connect('clicked', self.nav)
        self.back.set_sensitive(False)

        header = Gtk.HeaderBar()
        header.set_title("Software Center")
        header.set_show_close_button(True)
        header.show_all()
        header.pack_start(self.back)
        self.switcher = Gtk.StackSwitcher()
        self.switcher.set_stack(self.stack_main)
        header.set_custom_title(self.switcher)
        self.switcher.show_all()

        simg = Gtk.Image.new_from_icon_name("edit-find-symbolic", Gtk.IconSize.BUTTON)
        search_btn = Gtk.ToggleButton()
        search_btn.set_image(simg)
        search_btn.connect('clicked', self.s_handler)
        self.search_btn = search_btn
        header.pack_end(search_btn)
        self.set_titlebar(header)

        self.show_all()
        GObject.idle_add(self.update_count)

        if "--update" in sys.argv:
            self.stack_main.set_visible_child_name("updates")
        else:
            self.stack_main.set_visible_child_name("software")

    def s_handler(self, w):
        w.freeze_notify()
        self.search_bar.set_search_mode(w.get_active())
        w.thaw_notify()

    def init_css(self):
        ''' Temporary... '''
        css = Gtk.CssProvider()
        f = Gio.File.new_for_path("/usr/lib/evolve-sc/style.css")
        css.load_from_file(f)
        Gtk.StyleContext.add_provider_for_screen(self.get_screen(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def search_changed(self, w, data=None):
        if self.stack.get_visible_child_name() not in ["groups", "package"]:
            self.stack.set_visible_child_name("groups")
        if self.stack_main.get_visible_child_name() != "software":
            self.stack_main.set_visible_child_name("software")
        text = w.get_text().strip()
        if text == "":
            self.search_bar.set_search_mode(False)

        act =  False if text == "" else True
        self.search_btn.freeze_notify()
        self.search_btn.set_active(act)
        self.search_btn.thaw_notify()

        self.groups_page.searching(w)

    def do_apply(self, basket, e=None):
        self.stack.set_visible_child_name('groups')
        self.back.set_sensitive(False)
        self.search_entry.set_text("")

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
            self.stack_main.child_set_property(self.updates_view, "title", "Updates (%d)" % count)
        else:
            self.stack_main.child_set_property(self.updates_view, "title", "Updates")

    def nav(self, btn):
        vis = self.stack.get_visible_child_name()
        if (vis == self.old_view):
            vis = self.old_view = "groups"
        self.stack.set_visible_child_name(self.old_view)
        if self.old_view == "groups":
            self.back.set_sensitive(False)
        return

    def group_selected(self, groups_view, group):
        # Do not lock up for anyone :)
        self.old_view= self.stack.get_visible_child_name()
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
        self.old_view = self.stack.get_visible_child_name()
        self.stack.set_visible_child_name('package')
        self.back.set_sensitive(True)
        self.search_entry.set_text("")

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
