#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk


class ScSearchView(Gtk.Box):
    """ Provide search functionality

        Simple threaded search results page
    """

    __gtype_name__ = "ScSearchView"

    context = None

    def get_page_name(self):
        return _("Search")

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.context = context

        lab = Gtk.Label.new("Not yet implemented")
        self.pack_start(lab, True, True, 0)
        self.show_all()
