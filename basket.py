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

        self.title = Gtk.Label("<b>Software basket</b>")
        self.title.set_use_markup(True)
        self.pack_start(self.title, False, False, 0)
        
        self.set_border_width(10)

        self.removals = list()
        self.installs = list()
        self.updates = list()

    def update_label(self):
        self.title.set_markup("<b>Software basket: %d operations</b>" % self.operation_count())

    def operation_count(self):
        return len(self.removals) + len(self.installs) + len(self.updates)

    def remove_package(self, old_package):
        self.removals.append(old_package)
        self.update_label()

    def install_package(self, new_package):
        self.installs.append(new_package)
        self.update_label()

    def update_package(self, old_package, new_package):
        self.updates.append((old_package, new_package))
        self.update_label()
