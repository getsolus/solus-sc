#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk


class ScDrawer(Gtk.Box):
    """ Shows details for ongoing jobs

        The Drawer contains the drawer mechanism to show the ongoing jobs
        in the Software Center.
    """

    __gtype_name__ = "ScDrawer"

    context = None
    revealer = None
    sidebar = None

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)

        self.context = context

        self.revealer = Gtk.Revealer.new()
        self.pack_end(self.revealer, False, False, 0)
        self.build_sidebar()
        self.show_all()

        self.get_style_context().add_class("drawer-background")

        self.revealer.set_child_visible(False)

        self.set_visible(False)
        self.set_no_show_all(True)

    def build_sidebar(self):
        """ Build the actual sidebar """
        self.sidebar = Gtk.Label("Totally a sidebar =)")
        self.sidebar.get_style_context().add_class("drawer")
        self.revealer.add(self.sidebar)
