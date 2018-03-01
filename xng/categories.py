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


class ScCategoriesView(Gtk.Box):
    """ Transitioned from Home view to show a category """

    __gtype_name__ = "ScCategoriesView"

    context = None
    category = None

    def get_page_name(self):
        if not self.category:
            return "Categories"
        return self.category.get_name()

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.context = context

        self.layout_constraint = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.pack_start(self.layout_constraint, True, True, 0)
        self.layout_constraint.set_margin_start(40)
        self.layout_constraint.set_margin_top(40)
        self.layout_constraint.set_margin_bottom(40)

        # Mark the Categories view
        lab = Gtk.Label("Components")
        lab.get_style_context().add_class("sc-big")
        lab.set_margin_bottom(12)
        lab.set_halign(Gtk.Align.START)
        lab.set_use_markup(True)
        self.layout_constraint.pack_start(lab, False, False, 0)

        self.components = Gtk.FlowBox()
        self.components.set_selection_mode(Gtk.SelectionMode.NONE)
        self.layout_constraint.pack_start(self.components, False, False, 0)
        self.components.set_margin_bottom(42)
        self.components.set_margin_end(40)

        self.show_all()

    def set_category(self, category):
        """ Set the root level category """
        if category == self.category:
            return
        self.category = category

        # Clear out the old categories
        for sproglet in self.components.get_children():
            self.components.remove(sproglet)

        # Add all the new components
        for component in self.category.get_children():
            self.add_component(component)

    def add_component(self, component):
        """ Add a new component to the view for the toplevel parent """
        button = Gtk.Button.new_with_label(component.get_name())
        button.show_all()
        self.components.add(button)
