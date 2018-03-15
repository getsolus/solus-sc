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


class ScJobWidget(Gtk.Box):
    """ Provide a simple widget to provide information about jobs.
        Typically a JobWidget does nothing but show static information,
        however a special case instance is preserved forever to simplify
        updating the *current* job information
    """

    __gtype_name__ = "ScJobWidget"

    title_label = None
    action_label = None
    progressbar = None
    size_group = None

    def __init__(self, dynamic=False):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.set_spacing(3)
        self.set_property("margin", 4)

        self.size_group = Gtk.SizeGroup.new(Gtk.SizeGroupMode.HORIZONTAL)

        # Construct our title label.
        self.title_label = Gtk.Label.new("<small>{}</small>".format(
            "Update system software"))
        self.title_label.set_halign(Gtk.Align.START)
        self.title_label.set_property("xalign", 0.0)
        self.title_label.set_use_markup(True)
        self.pack_start(self.title_label, False, False, 0)
        self.size_group.add_widget(self.title_label)

        # No sense in creating widgets we never use.
        if not dynamic:
            return

        # Construct our ongoing action label
        self.action_label = Gtk.Label.new("<small>{}</small>".format(
            "Applying operation 25/50"))
        self.action_label.set_halign(Gtk.Align.START)
        self.action_label.set_property("xalign", 0.0)
        self.action_label.set_use_markup(True)
        self.action_label.get_style_context().add_class("dim-label")
        self.pack_start(self.action_label, False, False, 0)
        self.size_group.add_widget(self.action_label)

        # Construct our progress widget
        self.progressbar = Gtk.ProgressBar.new()
        self.progressbar.set_margin_top(2)
        self.progressbar.set_fraction(0.5)
        self.progressbar.set_halign(Gtk.Align.START)
        self.pack_start(self.progressbar, False, False, 0)
        self.size_group.add_widget(self.progressbar)
