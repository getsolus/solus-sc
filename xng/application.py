#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from .window import ScMainWindow
from gi.repository import Gio, Gtk, Gdk, GLib
from . import join_resource_path
import random
import time


SC_APP_ID = "com.solus_project.SoftwareCentre"


class ScApplication(Gtk.Application):

    app_window = None

    is_service_mode = False
    updates_view = False

    def activate_main_view(self):
        self.ensure_window()
        if self.updates_view:
            self.app_window.mode_open = "updates"
        else:
            self.app_window.mode_open = "home"
        self.app_window.present()

    def ensure_window(self):
        """ Ensure we have a window """
        if self.app_window is None:
            self.app_window = ScMainWindow(self)

    def startup(self, app):
        """ Main entry """
        self.init_css()

    def init_css(self):
        """ Set up the CSS before we throw any windows up """
        try:
            f = Gio.File.new_for_path(join_resource_path("styling.css"))
            css = Gtk.CssProvider()
            css.load_from_file(f)
            screen = Gdk.Screen.get_default()
            prio = Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            Gtk.StyleContext.add_provider_for_screen(screen,
                                                     css,
                                                     prio)
        except Exception as e:
            print("Error loading CSS: {}".format(e))

    def __init__(self):
        Gtk.Application.__init__(
            self,
            application_id=SC_APP_ID,
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.connect("activate", self.on_activate)
        self.connect("startup", self.startup)
        self.connect("command-line", self.handle_command_line)
        self.connect("handle-local-options", self.handle_local_options)

        option = GLib.OptionEntry()
        option.long_name = "update-view"
        option.short_name = 0
        option.flags = 0
        option.arg = GLib.OptionArg.NONE
        option.arg_data = None
        description = _("Open up the updates view of the application")
        option.description = description
        self.add_main_option_entries([option])

        # Make sure random is moar betterer
        random.seed(time.time())

    def on_activate(self, app):
        """ Activate the primary view """
        self.activate_main_view()

    def handle_command_line(self, app, cmdline):
        self.activate()
        return 0

    def handle_local_options(self, app, cmdline):
        if cmdline.contains("update-view"):
            self.updates_view = True
        return -1
