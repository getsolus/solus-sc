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

from gi.repository import Gtk, GLib


class ScSearchView(Gtk.VBox):
    """ Facilitate searching of the repo """

    flowbox = None
    owner = None
    search_box = None
    timeout_id = -1

    def __init__(self, owner):
        Gtk.EventBox.__init__(self)
        self.owner = owner

        self.search_box = Gtk.SearchEntry()
        self.search_box.set_property("margin", 20)
        self.search_box.connect("search-changed", self.on_search_changed)
        self.pack_start(self.search_box, False, False, 0)

    def on_search_changed(self, entry, udata=None):
        if self.timeout_id >= 0:
            GLib.source_remove(self.timeout_id)
            self.timeout_id = -1

        self.timeout_id = GLib.timeout_add(1000, self.begin_search)

    def begin_search(self):
        """ Search, but for realsies """
        txt = self.search_box.get_text()
        pkgs = self.owner.basket.packagedb.search_package([txt])
        print("{} results".format(len(pkgs)))
        self.timeout_id = -1
        return False
