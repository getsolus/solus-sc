#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  groups.py - SSC Group Navigation
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

class GroupsView(Gtk.VBox):

    __gsignals__ = {
        'group-selected': (GObject.SIGNAL_RUN_FIRST, None,
                          (str,))
    }
    
    def __init__(self, groups):
        Gtk.VBox.__init__(self)
        #self.set_border_width(20)

        self.grid = Gtk.Grid()
        self.grid.set_margin_top(80)
        self.pack_end(self.grid, True, True, 0)
        
        row = 0
        column = 0

        self.groups = groups
        group_names = self.groups.list_groups()
        max_columns = int(len(group_names) / 2)

        self.grid.set_border_width(40)
        row = 1
        column = 0
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

            btn.connect("clicked", lambda x: self.emit('group-selected', group))
            self.grid.attach(btn, column-1, row, 1, 1)
