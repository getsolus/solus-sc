#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2020 Solus
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import GLib, Gtk

APPS = {
    'android-studio':
        ('Android Studio', 'android-studio',
         'Android development environment based on IntelliJ IDEA.',
         'programming/android-studio/pspec.xml'),
    'bitwig-studio':
        ('Bitwig Studio', 'bitwig-studio',
         'Music production system for production, remixing and performance.',
         'multimedia/music/bitwig-studio/pspec.xml'),
    'enpass':
        ('Enpass', 'enpass',
         'A multiplatform password manager.',
         'security/enpass/pspec.xml'),
    'google-chrome-stable':
        ('Google Chrome', 'google-chrome',
         'The web browser from Google',
         'network/web/browser/google-chrome-stable/pspec.xml'),
    'google-chrome-beta':
        ('Google Chrome (Beta)', 'google-chrome-beta',
         'Beta channel for the web browser from Google',
         'network/web/browser/google-chrome-beta/pspec.xml'),
    'google-chrome-unstable':
        ('Google Chrome (Dev)', 'google-chrome-unstable',
         'Developer channel for the web browser from Google',
         'network/web/browser/google-chrome-unstable/pspec.xml'),
    'google-earth':
        ('Google Earth', 'google-earth',
         '3D interface for satellite imagery from Google',
         'network/web/google-earth/pspec.xml'),
    'gitkraken':
        ('GitKraken', 'gitkraken',
         'The downright luxurious Git client, for Windows, Mac and Linux',
         'programming/gitkraken/pspec.xml'),
    'idea':
        ('Idea', 'idea',
         'Idea - an IDE for the JVM Languages',
         'programming/idea/pspec.xml'),
    'insync':
        ('Insync', 'insync',
         'Insync extends Drive\'s web functionality to your desktop',
         'network/download/insync/pspec.xml'),
    'mendeleydesktop':
        ('Mendeley Desktop', 'mendeleydesktop',
         'Free reference manager and an academic social network.',
         'office/mendeleydesktop/pspec.xml'),
    'moneydance':
        ('Moneydance', 'moneydance',
         'A personal finance manager.',
         'office/moneydance/pspec.xml'),
    'ocenaudio':
        ('Ocenaudio', 'ocenaudio',
         'Ocenaudio is a fast, cross-platform audio editor.',
         'multimedia/music/ocenaudio/pspec.xml'),
    'plexmediaserver':
        ('Plex Media Server', 'plex',
         'Plex Media Server',
         'multimedia/video/plexmediaserver/pspec.xml'),
    'pycharm':
        ('Pycharm', 'pycharm',
         'An IDE for the Python Language.',
         'programming/pycharm/pspec.xml'),
    'pycharm-ce':
        ('Pycharm (Community Edition)', 'pycharm',
         'PyCharm Community Edition - an IDE for the Python',
         'programming/pycharm-ce/pspec.xml'),
    'rider':
        ('Rider', 'rider',
         'A cross-platform .NET IDE based on the IntelliJ platform and ReSharper.',
         'programming/rider/pspec.xml'),
    'rubymine':
        ('Rubymine', 'rubymine',
         'An IDE for the Ruby Language.',
         'programming/rubymine/pspec.xml'),
    'teamviewer':
        ('TeamViewer', 'teamviewer',
        'Application for remote control, desktop sharing, online meetings, web conferencing and file transfer between computers',
        'network/util/teamviewer/pspec.xml'),
    'slack-desktop':
        ('Slack', 'slack',
         'Team communication for the 21st century.',
         'network/im/slack-desktop/pspec.xml'),
    'spotify':
        ('Spotify', 'spotify',
         'Spotify Music, Video and Podcast Streaming Client.',
         'multimedia/music/spotify/pspec.xml'),
    'sublime-text':
        ('Sublime Text', 'sublime-text',
         'Sublime Text is a sophisticated text editor for code, markup and '
         'prose.',
         'programming/sublime-text/pspec.xml'),
    'viber':
        ('Viber', 'viber',
         'An instant messaging and VoIP app for various mobile operating '
         'systems.',
         'network/im/viber/pspec.xml'),
    'webstorm':
        ('Webstorm', 'webstorm',
         'WebStorm - an IDE for the Web',
         'programming/webstorm/pspec.xml'),
}


class ThirdPartyView(Gtk.VBox):
    """ Work around insane distribution policy to help the user. """

    theme = None
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
        self.theme = Gtk.IconTheme()
        self.theme.set_custom_theme("solus-sc")

        label = Gtk.Label(
            "<small>"
            "Software provided via the third party tooling will be fetched "
            "directly from the vendor and installed locally."
            "\nSolus Project accepts no responsibility for the content"
            " provided by these vendors.</small>\n")
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
        scroll.get_style_context().add_class("third-party-view")

        self.build_ui()

    def build_ui(self):
        for child in self.listbox.get_children():
            child.destroy()

        for key in sorted(APPS):
            row = APPS[key]

            hbox = Gtk.HBox(0)
            try:
                icon = self.theme.load_icon(row[1], 48, Gtk.IconLookupFlags.FORCE_SIZE)
                img = Gtk.Image.new_from_pixbuf(icon)
            except GLib.Error as err:
                img = Gtk.Image.new_from_icon_name(row[1], Gtk.IconSize.DIALOG)

            img.set_pixel_size(48)

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
                ibtn = Gtk.Button(_("Check for updates"))
            else:
                ibtn = Gtk.Button(_("Install"))
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
