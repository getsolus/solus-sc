#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  package_view.py - SSC Package Viewer
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
import time

import pisi.api

GENERIC = "package-x-generic"

def do_justif(label):
    label.set_alignment(0.0, 0.5)
    label.set_justify(Gtk.Justification.LEFT)

class PackageView(Gtk.VBox):

    __gsignals__ = {
        'operation-selected': (GObject.SIGNAL_RUN_FIRST, None,
                          (str,object,object))
    }

    def make_valid(self, istr):
        ret = istr.replace("&", "&amp;").replace("\"", "&quot;")
        return ret

    def __init__(self, packagedb, installdb):
        Gtk.VBox.__init__(self)

        self.set_border_width(10)
        
        self.packagedb = packagedb
        self.installdb = installdb

        self.title = Gtk.Label("")
        do_justif(self.title)

        self.header = Gtk.HBox()
        self.header.set_border_width(20)

        # Package's image
        self.image = Gtk.Image()

        self.pack_start(self.header, False, False, 0)
        self.header.pack_start(self.title, False, False, 5)

        self.desc = Gtk.Label("")
        self.desc.set_line_wrap(True)
        do_justif(self.desc)
        self.pack_start(self.desc, False, False, 0)

        sep = Gtk.Separator()
        self.pack_start(sep, False, True, 10)
        
        self.image_status = Gtk.Image()
        #self.header.pack_end(self.image_status, False, False, 0)
        self.header.pack_end(self.image, False, False, 0)

        # Begin serious business
        self.content_left = Gtk.VBox()
        self.content_right = Gtk.VBox()
        self.content_left.set_hexpand(False)
        
        hbox_control = Gtk.HBox()
        #hbox_control.pack_start(self.image_status, False, False, 4)

        self.control_button = Gtk.Button()
        self.control_button.connect("clicked", self._do_emit)
        self.status_label = Gtk.Label("")
        hbox_control.pack_start(self.status_label, False, False, 0)
        hbox_control.pack_end(self.control_button, False, False, 0)

        self.pack_start(hbox_control, False, False, 0)

        self.link = Gtk.LinkButton("about:solusos", "Visit homepage")
        self.link.set_hexpand(False)

        # Description
        self.description = Gtk.Label("")
        self.description.set_line_wrap(True)

        self.content_left.pack_start(self.description, False, False, 0)
        self.content_left.pack_start(self.link, False, False, 0)

        self.wrap = Gtk.HBox()
        self.wrap.pack_start(self.content_left, True, True, 0)
        self.wrap.pack_start(self.content_right, False, False, 0)

        self.pack_start(self.wrap, False, False, 20)

        # Last update
        self.update_label = Gtk.Label("")
        self.pack_start(self.update_label, False, False, 0)

        self.package = None


    def _do_emit(self, btn, data=None):
        self.emit('operation-selected', self.operation_type, self.package, self.old_package)

    def num_deps(self, package):
        deps = package.runtimeDependencies()
        count = 0
        for dep in deps:
            if not dep.satisfied_by_installed():
                count += 1
        return count

    def calculate_dependencies(self, package):
        dep_count = self.num_deps(package)
        if dep_count == 0:
            self.status_label.set_markup("<b>No extra dependencies required</b>")
        elif dep_count == 1:
            self.status_label.set_markup("<b>Requires %d extra package to be installed</b>" % dep_count)
        else:
            self.status_label.set_markup("<b>Requires %d packages to be installed</b>" % dep_count)

    def mark_selection(self, selection):
        if selection is None:
            self.set_from_package(self.package, self.old_package)
        else:
            self.control_button.set_label("Undo selection")
            self.operation_type = 'FORGET'

    def do_reset(self):
        if self.package is not None:
            self.package = self.packagedb.get_package(self.package.name)
            self.old_package = self.installdb.get_package(self.package.name) if self.installdb.has_package(self.package.name) else None

            self.set_from_package(self.package, self.old_package)

    def set_from_package(self, package, old_package):
        self.title.set_markup("<span font='30.5'>%s</span> - <big>%s</big>" % (package.name, package.version))

        self.update_label.set_visible(False)

        self.package = package
        self.old_package = old_package
        
        if old_package is not None:
            new_version = package.release
            old_version = old_package.release

            # Determine installation date
            info = self.installdb.get_info(package.name)
            date = time.asctime(info.time)
            
            if new_version > old_version:
                self.image_status.set_from_icon_name("package-installed-outdated", Gtk.IconSize.BUTTON)
                self.control_button.set_label("Update")
                self.status_label.set_markup("<b>You should update as a new version is available. You are currently using %s-%s</b>" % (old_package.version, old_package.release))
                update = package.history[0]
                msg = update.comment
                self.update_label.set_markup("<b>Update</b>\n%s" % msg)
                self.operation_type = 'UPDATE'
                #self.update_label.set_visible(True)
            else:
                self.image_status.set_from_icon_name("package-installed-updated", Gtk.IconSize.BUTTON)
                self.control_button.set_label("Uninstall")
                self.status_label.set_markup("<b>Installed on %s</b>" % date)
                self.operation_type = 'UNINSTALL'
        else:
            self.image_status.set_from_icon_name("package-available", Gtk.IconSize.LARGE_TOOLBAR)
            self.control_button.set_label("Install")

            self.status_label.set_markup("<b>Calculating dependencies...</b>")
            self.operation_type = 'INSTALL'
            GObject.idle_add(self.calculate_dependencies, package)

        self.desc.set_markup('<span font=\'30.5\'>“</span><i>  %s  </i><span font=\'30.5\'>”</span>' % self.make_valid(str(package.summary)))

        if package.source.homepage is not None:
            self.link.set_uri(package.source.homepage)
            self.link.set_visible(True)
        else:
            self.link.set_visible(False)

        if package.icon is not None:
            self.image.set_from_icon_name(package.icon, Gtk.IconSize.DIALOG)
        else:
            self.image.set_from_icon_name(GENERIC, Gtk.IconSize.DIALOG)
            
        self.description.set_markup(self.make_valid(str(package.description)))
