#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk


ICON_MAPS = {
    "desktop": "user-desktop",
    "desktop.budgie": "start-here-solus",
    "desktop.core": "system-run",
    "desktop.font": "font-ttf",
    "desktop.gnome": "desktop-environment-gnome",
    "desktop.gnome.core": "system-devices-information",
    "desktop.gnome.doc": "folder-documents",
    "desktop.gtk": "gtk-dialog-info",
    "desktop.kde": "kde",
    "desktop.library": "emblem-shared-symbolic",
    "desktop.mate": "mate",
    "desktop.multimedia": "multimedia-volume-control",
    "desktop.qt": "qtconfig-qt4",
    "desktop.theme": "preferences-desktop-wallpaper",
    "editor": "atom",
    "games": "applications-games",
    "games.action": "dota2",
    "games.arcade": "gnome-nibbles",
    "games.card": "gnome-aisleriot",
    "games.emulator": "ds-emulator",
    "games.puzzle": "gnome-tetravex",
    "games.rpg": "wesnoth",
    "games.strategy": "games-endturn",
    "multimedia.sound": "multimedia-volume-control",
    "multimedia.video": "folder-videos",
    "multimedia.audio": "folder-music",
    "multimedia.graphics": "folder-pictures",
    "network.download": "transmission",
    "network.email": "internet-mail",
    "network.im": "empathy",
    "network.irc": "hexchat",
    "network.news": "internet-news-reader",
    "network.web": "internet-web-browser",
    "network.web.browser": "firefox",
    "office": "libreoffice-calc",
    "office.finance": "homebank",
    "office.maths": "accessories-calculator",
    "office.scientific": "applications-science",
    "office.notes": "gnote",
    "office.viewers": "calibre-viewer",
    "programming.devel": "text-x-changelog",
    "programming.haskell": "text-x-haskell",
    "programming.ide": "accessories-text-editor",
    "programming.java": "text-x-java",
    "programming.perl": "application-x-perl",
    "programming.python": "application-x-python-bytecode",
    "programming.ruby": "application-x-ruby",
    "programming.tools": "gitg",
    "security": "security-high",
}

BREEZE_MISSING_COMP = {
    "desktop.gnome" : "package-x-generic",
    "desktop.gnome.core" : "package-x-generic",
    "desktop.gtk" : "package-x-generic",
    "desktop.mate" : "package-x-generic",
    "desktop.qt" : "package-x-generic",
    "games.action": "blinken",
    "games.arcade": "kolf",
    "games.card" : "kpat",
    "games.emulator": "input-gaming",
    "games.puzzle" : "kblocks",
    "network.download" : "kget",
    "network.email": "kmail",
    "network.news" : "quiterss",
    "network.web.browser": "konqueror",
    "office.notes" : "knotes"
}


class ScComponentButton(Gtk.Button):
    """ Manage the monotony of a button """

    component = None

    def __init__(self, db, component, icon_theme_name):
        Gtk.Button.__init__(self)

        self.component = component

        c_desc = str(component.localName)
        if component.name in ICON_MAPS:
            icon = ICON_MAPS[component.name]

            if icon_theme_name == "breeze": # If breeze
                if component.name in BREEZE_MISSING_COMP: # We're missing an icon here
                    icon = BREEZE_MISSING_COMP[component.name]
        else:
            icon = "package-x-generic"
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.SMALL_TOOLBAR)

        image.set_halign(Gtk.Align.START)
        image.set_pixel_size(16)

        label_box = Gtk.VBox(0)

        box = Gtk.HBox(0)
        box.pack_start(image, False, False, 0)
        image.set_property("margin-right", 10)
        label = Gtk.Label(c_desc)
        label.get_style_context().add_class("title")
        label.set_halign(Gtk.Align.START)
        label.set_valign(Gtk.Align.START)
        label_box.pack_start(label, True, True, 0)
        box.pack_start(label_box, True, True, 0)
        # self.set_relief(Gtk.ReliefStyle.NONE)
        self.add(box)

        # count the components
        count = len(db.get_packages(component.name))
        info_label = Gtk.Label(str(count))
        info_label.set_halign(Gtk.Align.START)
        info_label.get_style_context().add_class("info-label")
        info_label.get_style_context().add_class("dim-label")
        # label_box.pack_start(info_label, False, False, 0)

        self.get_style_context().add_class("group-button")


class ScComponentsView(Gtk.EventBox):
    """ Main group view, i.e. "System", "Development", etc. """

    label = None
    flowbox = None
    owner = None
    groups_view = None

    def __init__(self, groups_view, owner):
        Gtk.EventBox.__init__(self)
        self.owner = owner
        self.groups_view = groups_view

        self.scroll = Gtk.ScrolledWindow(None, None)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.add(self.scroll)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_property("margin", 20)
        self.flowbox.set_column_spacing(15)
        self.flowbox.set_row_spacing(15)
        self.flowbox.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_valign(Gtk.Align.START)
        self.scroll.add(self.flowbox)

    def set_components(self, components, icon_theme_name):
        """ Update our view based on a given set of components """
        for widget in self.flowbox.get_children():
            widget.destroy()
        compdb = self.owner.basket.componentdb
        appends = []

        for comp in components:
            component = compdb.get_component(comp)
            appends.append(component)

        for component in sorted(appends, key=lambda x: x.localName):
            btn = ScComponentButton(compdb, component, icon_theme_name)
            btn.connect("clicked", self.on_clicked)
            self.flowbox.add(btn)
            btn.show_all()

    def on_clicked(self, btn, udata=None):
        component = btn.component
        self.groups_view.select_component(component)
