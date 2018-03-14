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

from gi.repository import Gtk, GObject


class ScSettingsView(Gtk.Box):
    """ Enable controlling the Software Center settings from the sidebar
    """

    __gtype_name__ = "ScSettingsView"

    context = None

    __gsignals__ = {
        'go-back': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
    }

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.context = context

        self.build_header()

        lab = Gtk.Label.new("Not yet implemented")
        self.pack_start(lab, True, True, 0)
        self.show_all()

        self.set_border_width(10)

    def build_header(self):
        """ Match header area of main view to allow back button """
        # Link to get to settings view
        button = Gtk.Button.new()
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

        self.pack_start(button, False, False, 0)

    def on_back_clicked(self, btn, udata=None):
        """ User clicked our back button, let the primary view know """
        self.emit('go-back')
