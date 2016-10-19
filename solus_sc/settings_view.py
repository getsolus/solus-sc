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

from gi.repository import Gtk
from . import join_resource_path


class ScSettingsView(Gtk.EventBox):
    """ Settings for updates, etc """

    def can_back(self):
        """ Whether we can go back """
        return False

    def __init__(self, owner):
        Gtk.EventBox.__init__(self)

        builder = Gtk.Builder()
        rp = join_resource_path("settings.ui")

        builder.add_from_file(rp)

        main_grid = builder.get_object("main_grid")

        self.add(main_grid)
