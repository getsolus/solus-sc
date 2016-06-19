#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2016 Ikey Doherty <ikey@solus-project.com>
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
    basket = None

    def on_basket_changed(self, basket, udata=None):
        sensitive = not basket.is_busy()
        if sensitive and not self.listbox.get_sensitive():
            self.build_ui()
        self.listbox.set_sensitive(sensitive)

    def __init__(self, owner):
        Gtk.VBox.__init__(self)
        self.basket = owner.basket
        self.basket.connect("basket-changed", self.on_basket_changed)

        label = Gtk.Label(
            "<small>"
            "Software provided via the third party tooling will be fetched "
            "directly from the vendor and installed locally."
            "\nSolus Project accepts no responsibility for the content"
            " provided by these vendors.\n"
            "If your software is listed here and you want it in our main "
            "channels, then please <a href='{}'>contact us</a>."
            "</small>".format(
                "mailto:root@solus-project.com?subject=repo-promotion"))
        label.set_use_markup(True)
        self.pack_end(label, False, False, 0)
        label.set_property("margin-start", 20)
        label.set_property("margin-top", 10)
        label.set_property("margin-bottom", 10)
        label.set_halign(Gtk.Align.START)

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll = Gtk.ScrolledWindow(None, None)
        self.pack_start(scroll, True, True, 0)
        scroll.add(self.listbox)
        scroll.set_shadow_type(Gtk.ShadowType.ETCHED_IN)

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

            ibtn = None
            if self.basket.installdb.has_package(key):
                ibtn = Gtk.Button("Check for updates")
            else:
                ibtn = Gtk.Button("Install")
            ibtn.get_style_context().add_class("suggested-action")
            ibtn.set_halign(Gtk.Align.END)
            ibtn.set_valign(Gtk.Align.CENTER)
            hbox.pack_end(ibtn, False, False, 0)
            ibtn.set_property("margin", 6)

            # Runtime-mark it
            ibtn.package_name = key
            ibtn.connect("clicked", self.on_install_clicked)

            hbox.show_all()
            self.listbox.add(hbox)

    def on_install_clicked(self, btn, udata=None):
        """ Proxy the call """
        self.basket.build_package(btn.package_name)
