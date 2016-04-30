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


class ScSidebar(Gtk.VBox):

    size_group = None

    def __init__(self):
        Gtk.VBox.__init__(self, 0)

        self.size_group = Gtk.SizeGroup(Gtk.SizeGroupMode.BOTH)
