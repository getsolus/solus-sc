#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk
# from xng.plugins.base import PopulationFilter


class ScHomeView(Gtk.Box):

    context = None
    categories = None

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.context = context
        self.context.connect('loaded', self.on_context_loaded)

        self.categories = Gtk.FlowBox()
        self.pack_start(self.categories, True, True, 0)

        self.show_all()

    def on_context_loaded(self, context):
        """ Fill the categories """
        for plugin in self.context.plugins:
            for cat in plugin.categories():
                self.add_category(plugin, cat)

    def add_category(self, plugin, category):
        button = Gtk.Button(category.get_name())
        button.show_all()
        self.categories.add(button)
