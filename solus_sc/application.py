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
from .monitor import ScMonitor
from .tray import ScTray
from gi.repository import Gio, Gtk, Gdk

import os

SC_APP_ID = "com.solus_project.SoftwareCenter"


class ScApplication(Gtk.Application):

    app_window = None
    monitor = None
    tray_icon = None

    is_service_mode = False

    def request_quit(self):
        """ TODO: Something more clever. """
        self.quit()

    def window_closed(self):
        """ Child informed us that they closed """
        print("Child removed!")
        self.app_window = None

    def activate_main_view(self):
        self.ensure_window()
        self.app_window.mode_open = "home"
        self.app_window.present()

    def ensure_window(self):
        """ Ensure we have a window """
        if self.app_window is None:
            self.app_window = ScMainWindow(self)

    def action_show_updates(self, action, param):
        """ Open the updates view """
        self.ensure_window()
        self.app_window.mode_open = "updates"
        was_visible = self.app_window.get_visible()
        self.app_window.present()
        if was_visible:
            self.app_window.show_updates()

    def init_actions(self):
        """ Initialise our action maps """
        action = Gio.SimpleAction.new("show-updates", None)
        action.connect("activate", self.action_show_updates)

        self.add_action(action)

    def startup(self, app):
        """ Main entry """
        print("I am now doing the motions of the startupings")
        self.init_css()
        if self.get_flags() & Gio.ApplicationFlags.IS_SERVICE:
            print("Running in service mode")
            self.is_service_mode = True

        self.init_actions()
        self.monitor = ScMonitor(app)
        self.tray_icon = ScTray(self)
        self.hold()

    def shutdown(self, app):
        print("I am now doing the motions of the shutdownings")

    def init_css(self):
        """ Set up the CSS before we throw any windows up """
        try:
            our_dir = os.path.dirname(os.path.abspath(__file__))
            f = Gio.File.new_for_path(os.path.join(our_dir, "styling.css"))
            css = Gtk.CssProvider()
            css.load_from_file(f)
            prio = Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(),
                                                     css,
                                                     prio)
        except Exception as e:
            print("Error loading CSS: {}".format(e))

    def __init__(self):
        Gtk.Application.__init__(self,
                                 application_id=SC_APP_ID,
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)
        self.connect("startup", self.startup)
        self.connect("shutdown", self.shutdown)

    def on_activate(self, app):
        """ Activate the primary view """
        self.activate_main_view()
