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

from .card import ScCard


class ScUpdatesView(Gtk.Box):
    """ Show system and application updates

        The updates view provides an overview of available updates and provides
        an easy mechanism for users to apply them.
    """

    __gtype_name__ = "ScUpdatesView"

    context = None

    def get_page_name(self):
        return _("Updates")

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.context = context

        self.build_stats_view()

        lab = Gtk.Label.new("Not yet implemented")
        lab.get_style_context().add_class("dim-label")
        self.pack_start(lab, True, True, 0)
        self.show_all()

    def build_stats_view(self):
        """ Build the assortment of stats we show at the top of the page """
        flowbox = Gtk.FlowBox.new()
        flowbox.set_homogeneous(True)
        flowbox.set_row_spacing(24)
        flowbox.set_column_spacing(24)
        flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.pack_start(flowbox, False, False, 0)
        flowbox.set_halign(Gtk.Align.CENTER)
        flowbox.set_hexpand(True)
        flowbox.set_property("margin", 24)

        # Primary update card
        card = ScCard()
        flowbox.add(card)
        card.set_title("Updates available")
        card.set_body("36")
        card.get_style_context().add_class("updates-card")
        card.set_icon_name("software-update-available-symbolic")

        # Bug count
        card = ScCard()
        flowbox.add(card)
        card.set_title("Bugs fixed")
        card.set_body("12")
        card.get_style_context().add_class("bugs-card")
        card.set_icon_name("edit-cut-symbolic")

        # Security count
        card = ScCard()
        flowbox.add(card)
        card.set_title("Security updates")
        card.set_body("15")
        card.get_style_context().add_class("security-card")
        card.set_icon_name("security-high-symbolic")
