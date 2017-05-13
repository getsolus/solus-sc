#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

# from gi.repository import AppStreamGlib as As
from gi.repository import Gtk


class ScImageWidget(Gtk.Frame):
    """ The ScImageWidget is used as the *main* screenshot that is currently
        shown for a given application. It is not the image *selector*
    """

    page_not_found = None
    page_image = None
    stack = None

    def __init__(self):
        Gtk.Frame.__init__(self)

        self.stack = Gtk.Stack.new()
        self.add(self.stack)
        self.set_border_width(0)
        self.set_property("margin", 0)
        self.set_shadow_type(Gtk.ShadowType.NONE)

        self.create_page_not_found()
        self.create_page_image()

        self.show_all()

        self.stack.set_visible_child_name("page-not-found")

    def create_page_not_found(self):
        """ Construct the "no screenshot available" page """
        self.page_not_found = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.stack.add_named(self.page_not_found, "page-not-found")

        self.page_not_found.set_valign(Gtk.Align.CENTER)
        self.page_not_found.set_halign(Gtk.Align.CENTER)

        img = Gtk.Image.new_from_icon_name(
            "image-missing-symbolic", Gtk.IconSize.DIALOG)
        self.page_not_found.pack_start(img, False, False, 0)
        img.get_style_context().add_class("dim-label")
        img.set_margin_end(15)

        lab = Gtk.Label.new("<span size='x-large'>{}</span>".format(
            _("No screenshots available")))
        lab.set_use_markup(True)
        lab.get_style_context().add_class("dim-label")
        self.page_not_found.pack_start(lab, False, False, 0)

    def create_page_image(self):
        """ The main image preview. """
        self.page_image = Gtk.Image.new()
        self.stack.add_named(self.page_image, "page-image")
