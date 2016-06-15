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


class ScComponentsView(Gtk.EventBox):
    """ Main group view, i.e. "System", "Development", etc. """

    label = None
    flowbox = None
    owner = None

    def __init__(self, owner):
        Gtk.EventBox.__init__(self)
        self.owner = owner

        self.scroll = Gtk.ScrolledWindow(None, None)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.add(self.scroll)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_property("margin-start", 40)
        self.flowbox.set_property("margin-end", 40)
        self.flowbox.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_valign(Gtk.Align.START)
        self.scroll.add(self.flowbox)

    def set_components(self, components):
        """ Update our view based on a given set of components """
        for widget in self.flowbox.get_children():
            widget.destroy()
        compdb = self.owner.basket.componentdb
        for comp in components:
            component = compdb.get_component(comp)
            btn = Gtk.Button(component.localName)
            self.flowbox.add(btn)
            btn.show_all()
