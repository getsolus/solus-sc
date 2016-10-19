#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk, Gio
from . import join_resource_path


UPDATE_TYPE_ALL = 1
UPDATE_TYPE_SECURITY = 2
UPDATE_TYPE_MANDATORY = 4

# Precomputed "next check" times
UPDATE_DELTA_HOUR = 60 * 60
UPDATE_DELTA_DAILY = UPDATE_DELTA_HOUR * 24
UPDATE_DELTA_WEEKLY = UPDATE_DELTA_DAILY * 7


class ScSettingsView(Gtk.EventBox):
    """ Settings for updates, etc """

    settings = None
    check_button = None

    def can_back(self):
        """ Whether we can go back """
        return False

    def __init__(self, owner):
        Gtk.EventBox.__init__(self)

        builder = Gtk.Builder()
        rp = join_resource_path("settings.ui")

        builder.add_from_file(rp)

        # Main view itself
        main_grid = builder.get_object("main_grid")
        main_grid.reparent(self)

        # Check for updates
        self.check_button = builder.get_object("switch_check_updates")

        # Hook up settings
        self.settings = Gio.Settings.new("com.solus-project.software-center")
        self.settings.bind("check-updates",
                           self.check_button, "active",
                           Gio.SettingsBindFlags.DEFAULT)

        # Update frequency
        combo = builder.get_object("combo_frequency")
        model = Gtk.ListStore(str, str)
        model.append(["Every hour", "hourly"])
        model.append(["Daily", "daily"])
        model.append(["Weekly", "weekly"])
        combo.set_id_column(1)
        combo.set_model(model)
        renderer_text = Gtk.CellRendererText()
        combo.pack_start(renderer_text, True)
        combo.add_attribute(renderer_text, "text", 0)

        # Connect to enum settings
        self.settings.bind("update-frequency",
                           combo, "active-id", Gio.SettingsBindFlags.DEFAULT)

        self.settings.connect("changed", self.on_settings_changed)

    def on_settings_changed(self, key, udata=None):
        """ Handle settings changes """
        pass
