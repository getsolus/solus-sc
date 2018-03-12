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

from .loadpage import ScLoadingPage


class ScSearchView(Gtk.Box):
    """ Provide search functionality

        Simple threaded search results page
    """

    __gtype_name__ = "ScSearchView"

    context = None
    load = None

    def get_page_name(self):
        return _("Search")

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.context = context

        # Main swap stack
        self.stack = Gtk.Stack.new()
        self.stack.set_homogeneous(False)
        self.stack.set_transition_type(
            Gtk.StackTransitionType.CROSSFADE)

        self.pack_start(self.stack, True, True, 0)

        # Hook up our load page
        self.load = ScLoadingPage()
        self.load.set_message(_("Concentrating really hard"))
        self.stack.add_named(self.load, 'loading')

    def set_search_term(self, term):
        print("Search term is '{}'".format(term))
