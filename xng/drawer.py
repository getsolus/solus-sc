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
from .settings_view import ScSettingsView
from .jobview import ScJobView


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
        self.set_transition_duration(190)

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

        # Allow clicks outside the sidebar to trigger a dismissal
        self.connect('button-press-event', self.on_button_press_event)

        # Fix visibility now
        self.set_reveal_child(False)
        self.show_all()
        self.set_no_show_all(True)
        self.hide()

    def handle_key_event(self, e):
        """ Allow chaining global input to us """

        # Not relevant to us
        if not self.drawer_visible:
            return Gdk.EVENT_PROPAGATE

        # Not an escape..
        if e.keyval != Gdk.KEY_Escape:
            return Gdk.EVENT_PROPAGATE

        # We need to handle going back
        self.perform_back()
        return Gdk.EVENT_STOP

    def perform_back(self):
        """ Handle back navigation with the escape key """
        if not self.drawer_visible:
            return
        if self.drawer.handle_back():
            return
        # Dismiss!
        self.slide_out()

    def on_button_press_event(self, widget, udata=None):
        """ Handle modality of the sidebar """

        # Already handled in toplevel window for back button
        if udata.button == 8:
            return Gdk.EVENT_PROPAGATE

        # Because GTK positioning is utterly broken, our x y is relative
        # only to the WIDGET not the WINDOW. -_- Instead, transform to the
        # toplevel coordinate system, and then find out where the sidebar
        # is physically on screen, *then* compare root X.
        toplevel = self.get_toplevel()
        topwin = toplevel.get_window()
        (x, y) = topwin.get_position()
        (w, h) = toplevel.get_size()
        (rx, ry) = self.translate_coordinates(toplevel, x, y)
        child_x = (rx + w) - self.drawer.get_allocated_width()

        if udata.x_root >= rx and udata.x_root <= child_x:
            self.slide_out()
            return Gdk.EVENT_STOP

        return Gdk.EVENT_PROPAGATE

    def open_plan_view(self):
        self.slide_in()
        self.drawer.open_plan_view()

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
    stack = None

    settings_view = None
    job_view = None

    button_stack = None  # Settings, Back

    def __init__(self, context):
        Gtk.Revealer.__init__(self)

        self.context = context
        self.set_transition_duration(170)
        self.set_border_width(0)
        self.set_property("margin", 0)

        self.set_halign(Gtk.Align.END)
        self.set_valign(Gtk.Align.FILL)
        self.build_sidebar()
        self.show_all()

        self.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_LEFT)

    def build_sidebar(self):
        """ Build the actual sidebar """

        self.sidebar = Gtk.EventBox.new()
        self.sidebar.get_style_context().add_class("sidebar")

        self.layout = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.sidebar.add(self.layout)
        self.build_header()

        # Now add the stack
        self.stack = Gtk.Stack.new()
        self.stack.set_homogeneous(False)
        self.stack.set_interpolate_size(True)
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.layout.pack_start(self.stack, True, True, 0)

        # Build primary view
        self.build_primary_view()

        # Construct settings view to allow switching to it
        self.settings_view = ScSettingsView(self.context)
        self.stack.add_named(self.settings_view, 'settings')

        self.stack.add_named(self.context.plan_view, 'planner')

        self.sidebar.show_all()
        self.add(self.sidebar)

    def build_primary_view(self):
        """ Build the main page for the stack """
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.set_border_width(10)
        box.set_valign(Gtk.Align.FILL)
        box.set_vexpand(True)

        # Whack in the job view now
        self.job_view = ScJobView(self.context)
        box.pack_start(self.job_view, True, True, 0)

        # Now add to the stack
        box.show_all()
        self.stack.add_named(box, 'main')

    def build_header(self):
        """ Build the navigation stack header """
        # Link to get to settings view
        settings_button = Gtk.Button.new()
        settings_button.set_halign(Gtk.Align.END)
        settings_button.get_style_context().add_class("flat")
        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        button_img = Gtk.Image.new_from_icon_name(
            "system-run-symbolic",
            Gtk.IconSize.BUTTON)
        button_lbl = Gtk.Label.new(_("Settings"))
        button_box.pack_start(button_img, False, False, 0)
        button_img.set_margin_end(4)
        button_lbl.set_halign(Gtk.Align.START)
        button_box.pack_start(button_lbl, False, False, 0)
        settings_button.add(button_box)
        settings_button.connect('clicked', self.on_settings_clicked)

        # Link to get back to the main view
        button = Gtk.Button.new()
        button.set_halign(Gtk.Align.END)
        button.get_style_context().add_class("flat")
        button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        button_img = Gtk.Image.new_from_icon_name(
            "go-previous-symbolic",
            Gtk.IconSize.BUTTON)
        button_lbl = Gtk.Label.new(_("Back"))
        button_box.pack_start(button_img, False, False, 0)
        button_img.set_margin_end(4)
        button_lbl.set_halign(Gtk.Align.START)
        button_box.pack_start(button_lbl, False, False, 0)
        button.add(button_box)
        button.connect('clicked', self.on_back_clicked)

        # Now a button stack for our two buttons
        self.button_stack = Gtk.Stack.new()
        self.button_stack.set_interpolate_size(True)
        self.button_stack.set_transition_type(
            Gtk.StackTransitionType.CROSSFADE)
        self.button_stack.set_homogeneous(False)
        self.button_stack.set_halign(Gtk.Align.END)
        self.button_stack.set_margin_top(10)
        self.button_stack.set_margin_end(10)

        # Add buttons..
        self.button_stack.add_named(settings_button, 'settings_button')
        self.button_stack.add_named(button, 'back_button')
        self.button_stack.set_visible_child_name('settings_button')

        self.layout.pack_start(self.button_stack, False, False, 0)

        sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        sep.set_margin_top(6)
        sep.set_margin_bottom(18)
        self.layout.pack_start(sep, False, False, 0)

    def on_settings_clicked(self, widget, udata=None):
        """ Settings button was clicked, move to Settings view """
        self.stack.set_visible_child_name('settings')
        self.button_stack.set_visible_child_name('back_button')

    def on_back_clicked(self, widget, udata=None):
        """ Pressed back button from within settings view """
        self.stack.set_visible_child_name('main')
        self.button_stack.set_visible_child_name('settings_button')

    def slide_in(self):
        """ Slide ourselves onto the plane """
        self.set_reveal_child(True)

    def slide_out(self):
        """ Slide ourselves off the plane """
        self.set_reveal_child(False)
        # Reset on tween out
        self.stack.set_visible_child_name('main')
        self.button_stack.set_visible_child_name('settings_button')

    def handle_back(self):
        """ Allow back/escape behaviour """
        if self.stack.get_visible_child_name() == "main":
            return False
        self.on_back_clicked(None)
        return True

    def open_plan_view(self):
        """ Open to the plan view """
        self.stack.set_visible_child_name('planner')
        # TODO: Have a close button instead!
        self.button_stack.set_visible_child_name('back_button')
