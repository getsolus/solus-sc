#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk

APPS = {
    'spotify':
        ('Spotify', 'spotify',
         'Spotify Music, Video and Podcast Streaming Client.',
         'multimedia/music/spotify/pspec.xml'),
    'google-chrome-stable':
        ('Google Chrome', 'google-chrome',
         'The web browser from Google',
         'network/web/browser/google-chrome-stable/pspec.xml'),
}


class ThirdPartyView(Gtk.VBox):
    """ Work around insane distribution policy to help the user. """

    listbox = None

    def __init__(self, owner):
        Gtk.VBox.__init__(self)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll = Gtk.ScrolledWindow(None, None)
        self.pack_start(scroll, True, True, 0)
        scroll.add(self.listbox)

        self.build_ui()

    def build_ui(self):
        for child in self.listbox.get_children():
            child.destroy()

        for key in APPS:
            row = APPS[key]

            hbox = Gtk.HBox(0)
            img = Gtk.Image.new_from_icon_name(row[1], Gtk.IconSize.DIALOG)
            hbox.pack_start(img, False, False, 0)
            img.set_property("margin", 6)

            nom_box = Gtk.Label("<big>{}</big>\n{}".format(row[0], row[2]))
            nom_box.set_use_markup(True)
            nom_box.set_line_wrap(True)
            nom_box.set_property("xalign", 0.0)
            nom_box.set_property("margin", 6)
            hbox.pack_start(nom_box, True, True, 0)

            self.listbox.add(hbox)
