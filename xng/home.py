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


class ScTileButton(Gtk.Button):

    category = None

    def __init__(self, cat):
        Gtk.Button.__init__(self)
        self.category = cat

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.add(box)

        lab = Gtk.Label(self.category.get_name())
        lab.set_halign(Gtk.Align.START)
        box.pack_start(lab, True, True, 0)

        self.get_style_context().add_class("group-button")

        cats = cat.get_children()
        if len(cats) > 0:
            info = Gtk.Label("{} categories".format(len(cats)))
            info.set_halign(Gtk.Align.START)
            box.pack_start(info, False, False, 0)
            info.set_margin_top(2)
            info.get_style_context().add_class("dim-label")


class ScHomeView(Gtk.Box):

    context = None
    categories = None

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.context = context
        self.context.connect('loaded', self.on_context_loaded)

        self.categories = Gtk.FlowBox()
        self.categories.set_selection_mode(Gtk.SelectionMode.NONE)
        self.pack_start(self.categories, False, False, 0)

        self.set_border_width(40)
        self.show_all()

    def on_context_loaded(self, context):
        """ Fill the categories """
        for plugin in self.context.plugins:
            for cat in plugin.categories():
                self.add_category(plugin, cat)

    def add_category(self, plugin, category):
        button = ScTileButton(category)
        button.show_all()
        self.categories.add(button)
