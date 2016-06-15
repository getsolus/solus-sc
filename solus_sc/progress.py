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


class ScProgressWidget(Gtk.ActionBar):

    progressbar = None
    progresslabel = None

    def __init__(self):
        Gtk.ActionBar.__init__(self)

        self.progresslabel = Gtk.Label("Installing Google Chrome")
        self.progresslabel.set_valign(Gtk.Align.CENTER)
        self.progresslabel.set_halign(Gtk.Align.START)
        self.progresslabel.set_property("yalign", 0.5)
        self.progresslabel.set_property("xalign", 0.0)
        self.progresslabel.set_margin_start(6)
        self.progresslabel.set_margin_end(8)
        self.progresslabel.set_margin_top(4)
        self.progresslabel.set_margin_bottom(4)
        self.pack_start(self.progresslabel)
        self.progressbar = Gtk.ProgressBar()
        self.progressbar.set_fraction(0.6)
        self.progressbar.set_valign(Gtk.Align.CENTER)

        self.progressbar.set_hexpand(True)
        self.progressbar.set_margin_end(20)
        self.progressbar.set_margin_top(6)
        self.progressbar.set_margin_bottom(4)
        self.pack_start(self.progressbar)
