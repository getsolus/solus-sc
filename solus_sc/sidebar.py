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


class ScSidebar(Gtk.ListBox):

    def __init__(self):
        Gtk.ListBox.__init__(self)

        self.get_style_context().add_class("sidebar")

        items = [
            ("home", "Home", "user-home-symbolic"),
            ("updates", "Updates", "software-update-available-symbolic"),
            ("installed", "Installed", "system-software-install-symbolic"),
            ("3rd-party", "Third Party", "folder-download-symbolic"),
            ("settings", "Settings", "system-run-symbolic"),
        ]

        sel = None
        for item, label_sz, icon_sz in items:
            row = Gtk.HBox(0)
            label = Gtk.Label(label_sz)

            image = Gtk.Image.new_from_icon_name(icon_sz,
                                                 Gtk.IconSize.LARGE_TOOLBAR)
            row.pack_start(image, False, False, 0)
            image.set_property("margin-end", 5)
            label.set_property("margin-end", 5)
            row.pack_start(label, True, True, 0)
            label.set_halign(Gtk.Align.START)

            if sel is None:
                sel = row

            self.add(row)
        self.select_row(sel.get_parent())
