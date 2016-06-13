#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk
from gi.repository import Gio


class PackageDetailsView(Gtk.VBox):
    """ Show all the details of a given package to the user as well
        as supplying them with manipulation functions, i.e. for removal, etc
    """

    # The appsystem allows us to perform queries in icons and such
    appsystem = None

    # The main header icon, hopefully from appstream
    image_icon = None

    # Display name of the package, not necessarily the .eopkg name
    label_name = None

    # The currently selected package for rendering
    package = None

    # Description for this package. Currently stripped of markup..
    label_description = None

    def __init__(self, appsystem):
        Gtk.VBox.__init__(self)
        self.appsystem = appsystem

        self.set_border_width(12)

        header = Gtk.HBox(0)
        self.pack_start(header, False, False, 0)

        # Set up the icon
        self.image_icon = Gtk.Image.new()
        # Some padding between us and the display label..
        self.image_icon.set_margin_end(12)
        header.pack_start(self.image_icon, False, False, 0)

        # Set up the display label
        self.label_name = Gtk.Label("")
        header.pack_start(self.label_name, False, False, 0)
        self.label_name.set_halign(Gtk.Align.START)
        self.label_name.set_valign(Gtk.Align.CENTER)

        # Need the description down a bit and a fair bit padded
        self.label_description = Gtk.Label("")
        self.label_description.set_halign(Gtk.Align.START)
        self.label_description.set_valign(Gtk.Align.START)
        self.label_description.set_margin_top(20)
        # Deprecated but still needs using with linewrap
        self.label_description.set_property("xalign", 0.0)
        self.label_description.set_margin_start(8)
        # self.label_description.set_max_width_chars(1)
        self.label_description.set_line_wrap(True)
        self.pack_start(self.label_description, True, True, 0)

    def update_from_package(self, package):
        """ Update our view based on a given package """

        name = self.appsystem.get_name(package)
        comment = self.appsystem.get_summary(package)
        description = self.appsystem.get_description(package)

        # Update display now.
        title_format = "<span size='x-large'><b>{}</b></span>\n{}"
        self.label_name.set_markup(title_format.format(name, comment))

        # Sort out a nice icon
        pbuf = self.appsystem.get_pixbuf(package)
        if pbuf:
            # Handle icon theme names
            if isinstance(pbuf, Gio.ThemedIcon):
                self.image_icon.set_from_gicon(pbuf, Gtk.IconSize.DIALOG)
                self.image_icon.set_pixel_size(64)
            else:
                # Handle local files
                self.image_icon.set_from_pixbuf(pbuf)
        else:
            icon = self.appsystem.get_icon(package)
            self.image_icon.set_from_icon_name(icon, Gtk.IconSize.DIALOG)
            self.image_icon.set_pixel_size(64)

        # Update the description
        self.label_description.set_label(description)
