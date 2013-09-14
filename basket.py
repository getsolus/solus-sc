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

import comar

class BasketView(Gtk.VBox):
    
    def __init__(self, packagedb, installdb):
        Gtk.VBox.__init__(self)

        self.title = Gtk.Label("Software basket")
        self.title.set_use_markup(True)


        self.progress = Gtk.ProgressBar()
        self.revealer = Gtk.Revealer()
        self.revealer.add(self.progress)
        self.pack_start(self.revealer, False, False, 0)
        self.revealer.set_reveal_child(False)

        self.toolbar = Gtk.Toolbar()
        self.toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        label_item = Gtk.ToolItem()
        label_item.add(self.title)
        self.toolbar.add(label_item)

        self.pack_start(self.toolbar, False, False, 0)

        sep = Gtk.SeparatorToolItem()
        sep.set_expand(True)
        sep.set_draw(False)
        self.toolbar.add(sep)
        
        self.apply = Gtk.ToolButton("Apply")
        self.apply.set_label("Apply")
        self.apply.set_is_important(True)
        self.apply.set_icon_name("emblem-ok-symbolic")
        self.apply.connect("clicked", self.apply_operations)
        self.toolbar.add(self.apply)
        self.operations = dict()
        
        self.update_ui()

        self.cb = None
        self.link = comar.Link()
        self.pmanager = self.link.System.Manager['pisi']
        self.link.listenSignals("System.Manager", self.pisi_callback)

        self.current_operations = None

    def set_progress(self, fraction, label):
        if fraction is None:
            # Hide
            self.revealer.set_reveal_child(False)
            self.update_ui()
            return
        self.title.set_markup(label)
        self.revealer.set_reveal_child(True)
        self.progress.set_fraction(fraction)
        
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

    def pisi_callback(self, package, signal, args):

        print signal
        print args

        if signal == 'status':
            cmd = args[0]
            what = args[1]
            if cmd == 'updatingrepo':
                self.set_progress(1.0, "Updating %s repository" % what)
            elif cmd == 'extracting':
                self.set_progress(self.current_progress, "Extracting %s" % what)
                progress = (float(self.current_progress) / float(self.current_total))
                self.current_progress += 1
            elif cmd == 'configuring':
                progress = (float(self.current_progress) / float(self.current_total))
                self.current_progress += 1
                self.set_progress(self.current_progress, "Configuring %s" % what)
            elif cmd == 'upgraded':
                progress = (float(self.current_progress) / float(self.current_total))
                self.current_progress += 1
                self.set_progress(self.current_progress, "Upgraded %s" % what)

        if signal == 'progress':
            cmd = args[0]
            if cmd == 'fetching':
                self.set_progress(1.0, "Downloading %s" % args[1])
        elif signal == 'finished' or signal == None:
            if self.cb is not None:
                self.cb()
            self.cb = None
            self.set_progress(None,None)
            return

    def update_repo(self, cb=None):
        self.cb = cb
        self.pmanager.updateAllRepositories()

    def apply_operations(self, btn):
        updates = [i for i in self.operations if self.operations[i] == 'UPDATE']
        installs = [i for i in self.operations if self.operations[i] == 'INSTALL']
        removals = [i for i in self.operations if self.operations[i] == 'UNINSTALL']

        print "%d packages updated" % len(updates)
        print "%d packages installed" % len(installs)
        print "%d packages removed" % len(removals)

        # Install upgrades -_-
        self.current_operations = updates
        self.current_progress = 0
        self.current_total = len(self.current_operations) * 4 # Essentially 4 steps
        
        self.pmanager.updatePackage(",".join(updates), async=self.pisi_callback)
