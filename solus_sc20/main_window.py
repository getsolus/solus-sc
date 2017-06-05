#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk


class ScMainWindow(Gtk.ApplicationWindow):

    mode_open = None

    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self, application=app)

        self.app = app
        self.mode_open = "home"

        self.set_icon_name("system-software-install")
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        self.set_titlebar(headerbar)

        # Window title
        self.set_title(_("Software Center"))
        self.get_style_context().add_class("solus-sc")

        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_default_size(950, 650)

        self.show_all()
