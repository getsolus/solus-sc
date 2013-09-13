#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  interface.py - SSC Main Window
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
from gi.repository import Gtk

class SSCWindow(Gtk.Window):
    
    def __init__(self):
        Gtk.Window.__init__(self)
        
        self.set_title("Software")
        self.connect("destroy", Gtk.main_quit)
        self.set_size_request(700, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        
        # header area
        header = Gtk.Toolbar()
        header.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)

        # butt it all up to the end of the toolbar now
        sep = Gtk.SeparatorToolItem()
        sep.set_expand(True)
        sep.set_draw(False)
        header.add(sep)

        # search
        search = Gtk.ToolItem()
        search_entry = Gtk.Entry()
        search_entry.set_icon_from_icon_name(Gtk.EntryIconPosition.SECONDARY, "edit-find-symbolic")
        search.add(search_entry)
        seach.set_margin_right(3)
        header.add(search)
        layout = Gtk.VBox()
        layout.pack_start(header, False, False, 0)
        self.add(layout)
