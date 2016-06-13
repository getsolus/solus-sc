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
from gi.repository import AppStreamGlib as As


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

    install_button = None
    remove_button = None

    is_install_page = False

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
        self.label_name.set_max_width_chars(60)
        self.label_name.set_line_wrap(True)
        self.label_name.set_property("xalign", 0.0)
        header.pack_start(self.label_name, False, False, 0)
        self.label_name.set_halign(Gtk.Align.START)
        self.label_name.set_valign(Gtk.Align.START)
        self.label_name.set_margin_top(6)

        # Set up the action line
        action_line = Gtk.HBox(0)
        action_line.set_valign(Gtk.Align.CENTER)
        action_line.set_halign(Gtk.Align.END)
        header.pack_end(action_line, False, False, 0)
        self.install_button = Gtk.Button("Install")
        self.install_button.set_can_focus(False)
        self.install_button.get_style_context().add_class("suggested-action")
        action_line.pack_end(self.install_button, False, False, 0)
        self.install_button.set_no_show_all(True)

        # Remove button
        self.remove_button = Gtk.Button("Remove")
        self.remove_button.set_can_focus(False)
        self.remove_button.get_style_context().add_class("destructive-action")
        action_line.pack_end(self.remove_button, False, False, 0)
        self.remove_button.set_no_show_all(True)

        header.set_property("margin-bottom", 24)

        # Need the description down a bit and a fair bit padded
        self.label_description = Gtk.Label("")
        self.label_description.set_halign(Gtk.Align.START)
        self.label_description.set_valign(Gtk.Align.START)
        self.label_description.set_margin_top(20)
        # Deprecated but still needs using with linewrap
        self.label_description.set_property("xalign", 0.0)
        self.label_description.set_margin_start(8)
        self.label_description.set_max_width_chars(80)
        self.label_description.set_line_wrap(True)
        self.label_description.set_selectable(True)
        self.label_description.set_can_focus(False)
        self.pack_start(self.label_description, True, True, 0)

    def update_from_package(self, package):
        """ Update our view based on a given package """

        name = self.appsystem.get_name(package)
        comment = self.appsystem.get_summary(package)
        description = self.appsystem.get_description(package)

        version = "{}-{}".format(str(package.version), str(package.release))
        # Update display now.
        title_format = "<span size='x-large'><b>{}</b> - {}</span>\n{}"
        self.label_name.set_markup(title_format.format(name,
                                                       version,
                                                       comment))

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
        self.label_description.set_label(self.render_plain(description))

        # Take the appropriate action ..
        if self.is_install_page:
            self.remove_button.hide()
            self.install_button.show()
        else:
            self.install_button.hide()
            self.remove_button.show()

    def render_plain(self, input_string):
        """ Render a plain version of the description, no markdown """
        plain = As.markup_convert(input_string, -1,
                                  As.MarkupConvertFormat.SIMPLE)
        return plain
