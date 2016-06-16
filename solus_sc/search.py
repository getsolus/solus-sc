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


class ScSearchView(Gtk.VBox):
    """ Facilitate searching of the repo """

    flowbox = None
    owner = None
    search_box = None

    def __init__(self, owner):
        Gtk.EventBox.__init__(self)
        self.owner = owner

        hbox = Gtk.HBox(0)
        hbox.set_property("margin", 40)
        hbox.get_style_context().add_class("linked")
        self.pack_start(hbox, False, False, 0)
        self.search_box = Gtk.SearchEntry()

        search_button = Gtk.Button("Search")
        hbox.pack_start(self.search_box, True, True, 0)
        hbox.pack_end(search_button, False, False, 0)
