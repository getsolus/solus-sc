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

from gi.repository import Gtk, Gdk, GObject


class ScDrawer(Gtk.EventBox):
    """ Shows details for ongoing jobs

        The Drawer contains the drawer mechanism to show the ongoing jobs
        in the Software Center.
    """

    __gtype_name__ = "ScDrawer"

    context = None
    revealer = None
    sidebar = None

    drawer_visible = GObject.Property(type=bool, default=False)

    def __init__(self, context):
        Gtk.EventBox.__init__(self)

        self.context = context

        self.revealer = Gtk.Revealer.new()
        self.add(self.revealer)
        self.revealer.set_halign(Gtk.Align.END)
        self.revealer.set_valign(Gtk.Align.FILL)
        self.build_sidebar()
        self.show_all()

        self.get_style_context().add_class("drawer-background")
        self.revealer.set_reveal_child(False)
        self.revealer.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_LEFT)
        self.revealer.connect('notify::child-revealed', self.revealer_change)
        self.connect('button-press-event', self.on_button_press_event)

        self.set_no_show_all(True)
        self.hide()

    def revealer_change(self, revealer, prop):
        """ When the revealer hides the child, hide our own overlay self."""
        if revealer.get_reveal_child():
            return
        self.hide()

    def on_button_press_event(self, widget, udata=None):
        """ Handle modality of the sidebar """
        acqu = self.sidebar.get_allocation()
        salloc = self.get_allocation()
        acqu.x += salloc.x
        acqu.y += salloc.y
        if udata.x < acqu.x or udata.x > acqu.x + acqu.width:
            self.slide_out()
        elif udata.y < acqu.y or udata.y > acqu.y + acqu.height:
            self.slide_out()
        return Gdk.EVENT_PROPAGATE

    def build_sidebar(self):
        """ Build the actual sidebar """
        self.sidebar = Gtk.EventBox.new()
        self.sidebar.set_border_width(2)
        self.sidebar.get_style_context().add_class("sidebar")
        self.sidebar_label = Gtk.Label("Totally a sidebar =)")
        self.sidebar.add(self.sidebar_label)
        self.sidebar.show_all()
        self.revealer.add(self.sidebar)
        self.revealer.show_all()

    def slide_in(self):
        self.drawer_visible = True
        self.show()
        self.revealer.set_reveal_child(True)

    def slide_out(self):
        self.drawer_visible = False
        self.revealer.set_reveal_child(False)
