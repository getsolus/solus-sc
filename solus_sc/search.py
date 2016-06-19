#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk
from .search_results import ScSearchResults


class ScSearchView(Gtk.VBox):
    """ Facilitate searching of the repo """

    flowbox = None
    owner = None
    search_box = None
    search_results = None
    search_button = None

    def __init__(self, owner):
        Gtk.EventBox.__init__(self)
        self.owner = owner

        hbox = Gtk.HBox(0)
        hbox.set_property("margin", 40)
        hbox.get_style_context().add_class("linked")
        self.pack_start(hbox, False, False, 0)
        self.search_box = Gtk.SearchEntry()
        self.search_box.connect("changed", self.on_changed)
        self.search_box.connect("activate", self.on_clicked)

        self.search_button = Gtk.Button("Search")
        self.search_button.connect("clicked", self.on_clicked)
        hbox.pack_start(self.search_box, True, True, 0)
        hbox.pack_end(self.search_button, False, False, 0)
        self.search_button.set_sensitive(False)

        self.search_results = ScSearchResults(self.owner)
        self.pack_start(self.search_results, True, True, 0)

    def on_clicked(self, btn, udata=None):
        txt = self.search_box.get_text().strip()
        self.search_results.set_search_term(txt)

    def on_changed(self, entry, udata=None):
        txt = self.search_box.get_text().strip()

        if txt == "":
            self.search_button.set_sensitive(False)
            self.search_results.clear_view()
        else:
            self.search_button.set_sensitive(True)
