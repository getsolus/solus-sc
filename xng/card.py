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


class ScCard(Gtk.FlowBoxChild):
    """ A simplistic card used to display statistics and such in a pretty
        material design inspired fashion.
    """

    contents = None

    title_label = None
    body_label = None
    image = None
    image_wrap = None

    def __init__(self):
        Gtk.FlowBoxChild.__init__(self)

        # Ensure we set the outer card style
        self.get_style_context().add_class("sc-card")
        self.get_style_context().add_class("outer")
        self.set_border_width(0)
        self.set_property("margin", 0)

        self.set_size_request(300, -1)

        # Where we put stuff
        cwrap = Gtk.EventBox.new()
        cwrap.set_border_width(0)
        cwrap.set_property("margin", 0)

        # Primary contents view
        self.contents = Gtk.Grid.new()
        cwrap.add(self.contents)
        self.add(cwrap)
        cwrap.get_style_context().add_class("body")
        self.contents.set_column_spacing(12)
        self.contents.set_margin_end(6)

        # Build the image
        self.image = Gtk.Image.new_from_icon_name(
            "software-update-available-symbolic",
            Gtk.IconSize.DIALOG)
        self.image_wrap = Gtk.EventBox.new()
        self.image_wrap.set_border_width(0)
        self.image_wrap.set_property("margin", 0)
        self.image_wrap.get_style_context().add_class("image-wrap")
        self.image_wrap.add(self.image)
        self.image.set_property("margin", 6)
        self.image.set_valign(Gtk.Align.CENTER)
        self.image.set_halign(Gtk.Align.CENTER)
        self.contents.attach(self.image_wrap, 0, 0, 1, 2)
        self.image_wrap.set_margin_start(4)
        self.image_wrap.set_margin_top(4)
        self.image_wrap.set_margin_bottom(4)
        self.image_wrap.set_valign(Gtk.Align.CENTER)

        # Body label
        self.body_label = Gtk.Label.new("Body text")
        self.body_label.set_use_markup(True)
        self.body_label.set_halign(Gtk.Align.START)
        self.body_label.set_valign(Gtk.Align.END)
        self.contents.attach(self.body_label, 1, 0, 1, 1)
        self.body_label.get_style_context().add_class("body-label")

        # Title label
        self.title_label = Gtk.Label.new("Title")
        self.title_label.set_use_markup(True)
        self.title_label.get_style_context().add_class("title-label")
        self.title_label.get_style_context().add_class("dim-label")
        self.title_label.set_halign(Gtk.Align.START)
        self.title_label.set_valign(Gtk.Align.START)
        self.title_label.set_margin_end(6)
        self.contents.attach(self.title_label, 1, 1, 1, 1)

    def set_title(self, title):
        """ Set the title for this card """
        self.title_label.set_markup(title)

    def set_body(self, body):
        """ Set the body text for this card """
        self.body_label.set_markup(body)

    def set_icon_name(self, icon_name):
        self.image.set_from_icon_name(icon_name, Gtk.IconSize.LARGE_TOOLBAR)
