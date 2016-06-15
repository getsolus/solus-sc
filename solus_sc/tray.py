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


class ScTray(Gtk.StatusIcon):

    def __init__(self):
        Gtk.StatusIcon.__init__(self)
        self.set_from_icon_name("start-here-solus")
        self.set_visible(True)
        self.set_tooltip_text("Software Center")
