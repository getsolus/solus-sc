#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  package_view.py - SSC Package Viewer
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

class PackageView(Gtk.VBox):
    
    def __init__(self, packagedb, installdb):
        Gtk.VBox.__init__(self)

        self.set_border_width(10)
        
        self.packagedb = packagedb
        self.installdb = installdb

        self.title = Gtk.Label("")
        do_justif(self.title)

        self.header = Gtk.HBox()
        self.header.set_border_width(20)

        self.pack_start(self.header, False, False, 0)
        self.header.pack_start(self.title, False, False, 5)

        self.desc = Gtk.Label("")
        self.desc.set_line_wrap(True)
        do_justif(self.desc)
        self.pack_start(self.desc, False, False, 0)

        self.image_status = Gtk.Image()
        self.header.pack_end(self.image_status, False, False, 0)


    def set_from_package(self, package, old_package):
        self.title.set_markup("<span font='30.5'>%s</span> - <big>%s</big>" % (package.name, package.version))

        if old_package is not None:
            new_version = package.release
            old_version = old_package.release

            if new_version > old_version:
                self.image_status.set_from_icon_name("package-installed-outdated", Gtk.IconSize.LARGE_TOOLBAR)
            else:
                self.image_status.set_from_icon_name("package-installed-updated", Gtk.IconSize.LARGE_TOOLBAR)
        else:
            self.image_status.set_from_icon_name("package-available", Gtk.IconSize.LARGE_TOOLBAR)
        
        self.desc.set_markup('<span font=\'30.5\'>“</span><i>  %s  </i><span font=\'30.5\'>”</span>' % str(package.summary))
        pass
