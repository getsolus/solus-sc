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

from .main_window import ScMainWindow
from gi.repository import Gio, Gtk, Gdk

import os

SC_APP_ID = "com.solus_project.SoftwareCenter"


class ScApplication(Gtk.Application):

    app_window = None

    def init_css(self):
        """ Set up the CSS before we throw any windows up """
        try:
            our_dir = os.path.dirname(os.path.abspath(__file__))
            f = Gio.File.new_for_path(os.path.join(our_dir, "styling.css"))
            css = Gtk.CssProvider()
            css.load_from_file(f)
            Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css,
                                                     Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        except Exception as e:
            print("Error loading CSS: {}".format(e))

    def __init__(self):
        Gtk.Application.__init__(self,
                                 application_id=SC_APP_ID,
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        if self.app_window is None:
            self.init_css()
            self.app_window = ScMainWindow(self)
        self.app_window.present()
