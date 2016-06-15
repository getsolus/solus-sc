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


class ScComponentsView(Gtk.EventBox):
    """ Main group view, i.e. "System", "Development", etc. """

    label = None

    def __init__(self):
        Gtk.EventBox.__init__(self)

        self.label = Gtk.Label("")
        self.add(self.label)
        self.label.set_use_markup(True)

    def set_group(self, group):
        self.label.set_markup("<big>{}</big>".format(group))
