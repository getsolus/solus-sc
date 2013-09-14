#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  widgets.py - SSC Helper Widgets
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

import pisi.api

GENERIC = "package-x-generic"

def do_justif(label):
    label.set_alignment(0.0, 0.5)
    label.set_justify(Gtk.Justification.LEFT)

class PackageLabel(Gtk.VBox):

    __gsignals__ = {
        'operation-selected': (GObject.SIGNAL_RUN_FIRST, None,
                          (str,object,object))
    }

    def __init__(self, pkg, old_pkg, interactive=False):
        Gtk.VBox.__init__(self)

        self.set_border_width(4)
        self.header = Gtk.HBox()
        self.image = Gtk.Image()
        if pkg.icon is not None:
            self.image.set_from_icon_name(pkg.icon, Gtk.IconSize.DIALOG)
        else:
            self.image.set_from_icon_name(GENERIC, Gtk.IconSize.DIALOG)

        self.header.pack_start(self.image, False, False, 5)
        self.label_title = Gtk.Label("<b>%s</b> - <small>%s</small>\n%s" % (pkg.name, pkg.version, str(pkg.summary)))
        self.label_title.set_use_markup(True)
        do_justif(self.label_title)
        self.label_title.set_line_wrap(True)
        self.header.pack_start(self.label_title, False, False, 0)


        self.image_status = Gtk.Image()
        if interactive:
            btn = Gtk.Button()
            btn.add(self.image_status)
            btn.set_relief(Gtk.ReliefStyle.NONE)
            btn.connect("clicked", self.interactive_handler)
            self.header.pack_end(btn, False, False, 0)
        else:
            self.header.pack_end(self.image_status, False, False, 0)
        
        self.package = pkg
        self.old_package = old_pkg

        self.pack_start(self.header, True, True, 0)

    def interactive_handler(self, btn, data=None):
        status = self.package_status
        self.package_status = 'FORGET'
        self.mark_status(status)
        self.emit('operation-selected', status, self.package, self.old_package)
        
    def mark_status(self, status):
        if status == 'INSTALL':
            self.image_status.set_from_icon_name("package-install", Gtk.IconSize.SMALL_TOOLBAR)
        elif status == 'UNINSTALL':
            self.image_status.set_from_icon_name("package-remove", Gtk.IconSize.SMALL_TOOLBAR)
        elif status == 'UPDATE':
            self.image_status.set_from_icon_name("package-upgrade", Gtk.IconSize.SMALL_TOOLBAR)
        elif status == None or status == 'FORGET':
            self.reset_image()
        self.status = status
        
    def reset_image(self):
        if self.old_package is not None:
            new_version = self.package.release
            old_version = self.old_package.release

            if new_version > old_version:
                self.image_status.set_from_icon_name("package-installed-outdated", Gtk.IconSize.SMALL_TOOLBAR)
                self.package_status = 'UPDATE'
            else:
                self.image_status.set_from_icon_name("package-installed-updated", Gtk.IconSize.SMALL_TOOLBAR)
                self.package_status = 'UNINSTALL'
        else:
            self.image_status.set_from_icon_name("package-available", Gtk.IconSize.SMALL_TOOLBAR)
            self.package_status = 'INSTALL'
