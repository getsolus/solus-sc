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
from xng.plugins.base import PopulationFilter
from .featured import ScFeatured


class ScTileButton(Gtk.Button):

    category = None

    def __init__(self, cat):
        Gtk.Button.__init__(self)
        self.category = cat

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.add(box)

        # Just replace the icon on the fly with something that
        # fits better into the current theme
        icon_theme = self.get_settings().get_property("gtk-icon-theme-name")
        icon_theme = icon_theme.lower().replace("-", "")
        # Sneaky, I know.
        if icon_theme == "arcicons" or icon_theme == "arc":
            devIcon = "text-x-changelog"
        else:
            devIcon = "gnome-dev-computer"

        replacements = {
            "text-editor": "x-office-calendar",
            "redhat-programming": devIcon,
            "security-high": "preferences-system-privacy",
            "network": "preferences-system-network",
        }

        icon = self.category.get_icon_name()
        if icon in replacements:
            icon = replacements[icon]

        img = Gtk.Image.new_from_icon_name(
            icon,
            Gtk.IconSize.LARGE_TOOLBAR)
        img.set_margin_end(6)
        img.set_valign(Gtk.Align.CENTER)
        box.pack_start(img, False, False, 0)

        lab = Gtk.Label(self.category.get_name())
        lab.set_halign(Gtk.Align.START)
        lab.set_valign(Gtk.Align.CENTER)
        box.pack_start(lab, True, True, 0)

        self.get_style_context().add_class("group-button")
        self.get_style_context().add_class("flat")


class ScRecentButton(Gtk.Button):
    """ Prettified button to show a recently updated item """

    item = None

    def __init__(self, context, item):
        Gtk.Button.__init__(self)
        self.item = item

        st = self.get_style_context()
        st.add_class("flat")

        layout = Gtk.Grid()
        self.add(layout)

        id = item.get_id()
        name = context.appsystem.get_name(id, item.get_name())
        lab = Gtk.Label.new("<b>{}</b>".format(name))
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.START)

        pbuf = context.appsystem.get_pixbuf_only(id)
        img = Gtk.Image.new_from_pixbuf(pbuf)
        img.set_margin_end(12)

        layout.attach(img, 0, 0, 1, 2)
        layout.attach(lab, 1, 0, 1, 1)

        summary = context.appsystem.get_summary(id, item.get_summary())
        lab2 = Gtk.Label(summary)
        lab2.set_line_wrap(True)
        lab2.set_property("xalign", 0.0)
        lab2.set_width_chars(30)
        lab2.set_halign(Gtk.Align.START)
        lab2.set_valign(Gtk.Align.START)
        layout.attach(lab2, 1, 1, 1, 1)


class ScHomeView(Gtk.Box):

    context = None
    categories = None
    recents = None
    recents_home = None
    featured = None

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.context = context
        self.context.connect('loaded', self.on_context_loaded)

        self.featured = ScFeatured(self.context)
        self.pack_start(self.featured, False, False, 0)
        self.featured.set_margin_bottom(24)

        self.next_items = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.pack_start(self.next_items, True, True, 0)
        self.next_items.set_border_width(40)

        # Mark the Categories view
        lab = Gtk.Label("Categories")
        lab.get_style_context().add_class("sc-big")
        lab.set_margin_bottom(12)
        lab.set_halign(Gtk.Align.START)
        lab.set_use_markup(True)
        self.next_items.pack_start(lab, False, False, 0)

        self.categories = Gtk.FlowBox()
        self.categories.set_selection_mode(Gtk.SelectionMode.NONE)
        self.next_items.pack_start(self.categories, False, False, 0)
        self.categories.set_margin_bottom(42)

        # Mark the Recent view
        lab = Gtk.Label("Recently updated")
        lab.get_style_context().add_class("sc-big")
        lab.set_margin_top(12)
        lab.set_margin_bottom(12)
        lab.set_halign(Gtk.Align.START)
        lab.set_use_markup(True)

        # Somewhere to stuff the Recent rows
        self.recents = dict()
        self.next_items.pack_start(lab, False, False, 0)
        self.recents_home = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.next_items.pack_start(self.recents_home, False, False, 0)

        # self.set_border_width(40)
        self.show_all()

    def on_context_loaded(self, context):
        """ Fill the categories """
        for plugin in self.context.plugins:
            # Build the categories
            for cat in plugin.categories():
                self.add_category(plugin, cat)

            # Build the featured view
            plugin.populate_storage(
                self.featured, PopulationFilter.FEATURED,
                self.context.appsystem, None)

            # Build the recently updated view
            plugin.populate_storage(self, PopulationFilter.RECENT, None, None)

    def add_category(self, plugin, category):
        """ Add a main category to our view """
        button = ScTileButton(category)
        button.show_all()
        self.categories.add(button)

    def add_item(self, id, item, popfilter):
        if popfilter == PopulationFilter.RECENT:
            self.add_recent(item)

    def maybe_build_row(self, plugin):
        """ Find an appropriate Recent row for the plugin """
        if plugin in self.recents:
            return
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.set_property("margin", 4)
        box.set_margin_bottom(8)  # scrollbar = chunky
        scroll = Gtk.ScrolledWindow(None, None)
        scroll.add(box)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        scroll.set_kinetic_scrolling(True)
        scroll.show_all()
        self.recents_home.pack_start(scroll, False, False, 0)
        self.recents[plugin] = box

    def add_recent(self, item):
        """ Add recently updated item to the view """
        plugin = item.get_plugin()
        self.maybe_build_row(plugin)
        box = self.recents[plugin]

        button = ScRecentButton(self.context, item)
        button.show_all()
        box.pack_start(button, False, False, 12)
