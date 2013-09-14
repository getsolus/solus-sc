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

    __gsignals__ = {
        'basket-changed': (GObject.SIGNAL_RUN_FIRST, None,
                          (object,))
    }
    
    def __init__(self, packagedb, installdb):
        Gtk.VBox.__init__(self)

        self.packagedb = packagedb
        
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

        self.downloaded = 0
        self.current_package = None

    def set_progress(self, fraction, label):
        if fraction is None:
            # Hide
            self.revealer.set_reveal_child(False)
            self.update_ui()
            return
        print "%s %f" % (label, fraction)
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

    def _get_prog(self, step):  
        self.progress_current = step
        total = float(self.progress_total)
        current = float(self.progress_current)

        fract = float(current/total)
        return fract
        
    def pisi_callback(self, package, signal, args):
        if signal == 'status':
            cmd = args[0]
            what = args[1]
            if cmd == 'updatingrepo':
                self.set_progress(1.0, "Updating %s repository" % what)
            elif cmd == 'extracting':
                prog = self._get_prog(self.progress_current + self.step_offset)
                self.set_progress(prog, "Extracting %d of %d: %s" % (self.current_package, self.total_packages, what))
            elif cmd == 'configuring':
                prog = self._get_prog(self.progress_current + self.step_offset)
                self.set_progress(prog, "Configuring %d of %d: %s" % (self.current_package, self.total_packages, what))
            elif cmd in ['removing', 'installing']:
                prog = self._get_prog(self.progress_current + self.step_offset)
                lab = "Installing %s: %s"
                if cmd == 'removing':
                    lab = "Removing %s: %s"
                count = "%d of %d" % (self.current_package, self.total_packages)
                self.set_progress(prog, lab % (count, what))
            elif cmd in ['upgraded', 'installed', 'removed']:
                prog = self._get_prog(self.progress_current + self.step_offset)
                if cmd == 'upgraded':
                    lab = "Upgraded %s: %s"
                elif cmd == 'removed':
                    lab = "Removed %s: %s"
                elif cmd == 'installed':
                    lab = "Installed %s: %s"
                count = "%d of %d" % (self.current_package, self.total_packages)
                self.set_progress(prog, lab % (count, what))
                self.current_package += 1

        if signal == 'progress':
            cmd = args[0]
            if cmd == 'fetching':
                if self.current_operations is not None:
                    # Doing real operations now.
                    package = args[1]
                    whatisthis = args[2]
                    speed_number = args[3]
                    speed_label = args[4]
                    downloaded = args[5]
                    download_size = args[6]
                    down = downloaded
                    speed = "%d %s" % (speed_number, speed_label)

                    diff = downloaded - download_size
                    inc = self.total_size + diff
                    prog = self._get_prog(inc)

                    self.set_progress(prog, "Downloading %d of %d: %s (%s)" % (self.current_dl_package, self.total_packages, package, speed))

                    if downloaded >= download_size:
                        self.current_dl_package += 1
                else:
                    print args
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

    def get_sizes(self, packages):
        totalSize = 0
        packages = [self.packagedb.get_package(pkg) for pkg in packages]
        for package in packages:
            totalSize += package.packageSize
        return totalSize

    def invalidate_all(self):
        # Handle operations that finished.
        self.operations = list()
        self.emit('basket-changed', None)

    def apply_operations(self, btn):
        updates = [i for i in self.operations if self.operations[i] == 'UPDATE']
        installs = [i for i in self.operations if self.operations[i] == 'INSTALL']
        removals = [i for i in self.operations if self.operations[i] == 'UNINSTALL']

        STEPS = 4 # We monitor 4 post events

        print "%d packages updated" % len(updates)
        print "%d packages installed" % len(installs)
        print "%d packages removed" % len(removals)

        for packageset in [updates, installs, removals]:
            if len(packageset) == 0:
                continue
                
            self.current_package = 1
            self.current_dl_package = 1
            self.total_packages = len(packageset)
            
            if packageset != removals:
                self.total_size = self.get_sizes(packageset)
                self.step_offset = self.total_size / 10 # one tenth of progress is post install
                self.progress_total = self.total_size + ((self.step_offset * self.total_packages) * STEPS)
            else:
                self.total_size = self.total_packages * (STEPS / 2)
                self.step_offset = 1
                self.progress_total = self.total_size
            self.progress_current = 0

            self.current_operations = packageset

            self.cb = self.invalidate_all
            if packageset == updates:
                self.pmanager.updatePackage(",".join(packageset), async=self.pisi_callback)
            elif packageset == installs:
                self.pmanager.installPackage(",".join(packageset), async=self.pisi_callback)
            elif packageset == removals:
                self.pmanager.removePackage(",".join(packageset), async=self.pisi_callback)
