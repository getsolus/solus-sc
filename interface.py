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
import pisi.db.componentdb as componentdb


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
        search.set_margin_right(3)
        header.add(search)
        layout = Gtk.VBox()
        layout.pack_start(header, False, False, 0)
        self.add(layout)

        self.componentdb = componentdb.ComponentDB()
        self.components_view = Gtk.TreeView()
        ren = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Component", ren)
        column.add_attribute(ren, "markup", 0)
        self.components_view.append_column(column)

        scroller = Gtk.ScrolledWindow(None, None)
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroller.add(self.components_view)

        center = Gtk.HBox()
        center.pack_start(scroller, False, False, 0)
        layout.pack_start(center, True, True, 0)
        self.build_components()

    def build_components(self):
        store = Gtk.ListStore(str,str,object)
        for component_key in self.componentdb.list_components():
            component = self.componentdb.get_component(component_key)
            store.append([str(component.localName), str(component.description), component])
        store.set_sort_column_id(0, Gtk.SortType.ASCENDING)
        self.components_view.set_model(store)
        
