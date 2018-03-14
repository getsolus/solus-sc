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


class ScDrawerPlane(Gtk.Revealer):
    """ The Drawer Plane is the toplevel widget on the GtkOverlay allowing
        it to consume all input and contain an internal drawer that may
        be overlayed as part of the layout.

        Primarily this separate widget is used to enable a background opacity
        tween to provide a visual cue regarding modality in the stack.
    """

    __gtype_name__ = "ScDrawerPlane"

    context = None
    body = None
    drawer = None

    # Allow gobject bind to the sidebar button
    drawer_visible = GObject.Property(type=bool, default=False)

    def __init__(self, context):
        Gtk.Revealer.__init__(self)
        self.context = context

        # Ensure we consume the entire view
        self.set_halign(Gtk.Align.FILL)
        self.set_valign(Gtk.Align.FILL)

        # We want to crossfade our contents
        self.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)

        # Build the main body to show other things in
        self.body = Gtk.EventBox.new()
        self.body.get_style_context().add_class("drawer-background")
        self.add(self.body)

        # Plug the drawer into the body of the revealer
        self.drawer = ScDrawer(self.context)
        self.body.add(self.drawer)

        # Allow hiding ourselves as appropriate to fix input modality
        self.connect('notify::child-revealed', self.revealer_change)
        self.drawer.connect('notify::child-revealed', self.sidebar_change)

        # Fix visibility now
        self.set_reveal_child(False)
        self.show_all()
        self.set_no_show_all(True)
        self.hide()

    def slide_in(self):
        """ Activate plane and slide in the sidebar """
        self.show()
        self.drawer_visible = True
        self.set_reveal_child(True)

    def slide_out(self):
        """" Deactivate plane and slide out the sidebar """
        self.drawer_visible = False
        # Chains our own transition
        self.drawer.slide_out()

    def revealer_change(self, revealer, prop):
        """ When our content is visible, begin showing the child."""
        if self.get_reveal_child():
            # We're shown, so now we show the child drawer
            self.drawer.slide_in()
            return

        # Hide overlay self now
        self.hide()

    def sidebar_change(self, revealer, prop):
        """ The sidebar change,d so we can hide ourselves"""
        if revealer.get_reveal_child():
            return

        # Begin hiding ourselves now
        self.set_reveal_child(False)


class ScDrawer(Gtk.Revealer):
    """ Shows details for ongoing jobs

        The Drawer contains the drawer mechanism to show the ongoing jobs
        in the Software Center.
    """

    __gtype_name__ = "ScDrawer"

    context = None
    revealer = None
    sidebar = None

    def __init__(self, context):
        Gtk.Revealer.__init__(self)

        self.context = context

        self.set_halign(Gtk.Align.END)
        self.set_valign(Gtk.Align.FILL)
        self.build_sidebar()
        self.show_all()

        self.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_LEFT)

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
        self.sidebar_label = Gtk.Label("This is totally a sidebar =)")
        self.sidebar_label.set_property("margin", 5)
        self.sidebar.add(self.sidebar_label)
        self.sidebar.show_all()
        self.add(self.sidebar)

    def slide_in(self):
        """ Slide ourselves onto the plane """
        self.set_reveal_child(True)

    def slide_out(self):
        """ Slide ourselves off the plane """
        self.set_reveal_child(False)
