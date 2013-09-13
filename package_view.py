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

    __gsignals__ = {
        'package-selected': (GObject.SIGNAL_RUN_FIRST, None,
                          (object,object))
    }
    
    def __init__(self, packagedb, installdb):
        Gtk.VBox.__init__(self)

        self.set_border_width(20)
        self.packagedb = packagedb
        self.installdb = installdb

        self.title = Gtk.Label("")
        do_justif(self.title)

        self.pack_start(self.title, False, False, 5)

        self.desc = Gtk.Label("")
        self.desc.set_line_wrap(True)
        do_justif(self.desc)
        self.pack_start(self.desc, False, False, 0)

    def set_from_package(self, package, old_package):
        self.title.set_markup("<span font='30.5'>%s</span> - <big>%s</big>" % (package.name, package.version))

        self.desc.set_markup(str(package.description))
        pass
