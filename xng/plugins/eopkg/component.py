#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from ..base import ProviderCategory


class EopkgComponent(ProviderCategory):
    """ EopkgComponent belongs to a single EopkgGroup, providing navigational
        access to packages for a single exclusive component. This powers the
        primary view of the Software Center.
    """

    id = None
    comp = None

    def __init__(self, compID, comp):
        ProviderCategory.__init__(self)
        self.id = compID
        self.comp = comp

    def get_name(self):
        return str(self.comp.localName)

    def get_id(self):
        return str(self.id)

    def get_icon_name(self):
        if str(self.id) in ICON_MAPS:
            return ICON_MAPS[str(self.id)]
        return "package-x-generic"


# Utter laziness. :P
ICON_MAPS = {
    "desktop": "user-desktop",
    "desktop.budgie": "start-here-solus",
    "desktop.core": "system-run",
    "desktop.font": "fonts",
    "desktop.gnome": "desktop-environment-gnome",
    "desktop.gnome.core": "system-devices-information",
    "desktop.gnome.doc": "folder-documents",
    "desktop.gtk": "gtk-dialog-info",
    "desktop.kde": "desktop-environment-kde",
    "desktop.library": "emblem-shared-symbolic",
    "desktop.mate": "mate",
    "desktop.multimedia": "multimedia-volume-control",
    "desktop.qt": "qtconfig-qt4",
    "desktop.theme": "preferences-desktop-wallpaper",
    "editor": "x-office-document",
    "games": "applications-games",
    "games.action": "dota2",
    "games.arcade": "gnome-nibbles",
    "games.card": "gnome-aisleriot",
    "games.emulator": "ds-emulator",
    "games.puzzle": "gnome-tetravex",
    "games.rpg": "wesnoth",
    "games.strategy": "games-endturn",
    "multimedia.sound": "multimedia-volume-control",
    "multimedia.video": "camera-video",
    "multimedia.audio": "library-music",
    "multimedia.graphics": "camera-photo",
    "network.download": "transmission",
    "network.email": "internet-mail",
    "network.im": "empathy",
    "network.irc": "hexchat",
    "network.news": "internet-news-reader",
    "network.web": "emblem-web",
    "network.web.browser": "web-browser",
    "office": "x-office-spreadsheet",
    "office.finance": "homebank",
    "office.maths": "gnome-calculator",
    "office.scientific": "applications-science",
    "office.notes": "gnote",
    "office.viewers": "calibre-viewer",
    "programming.devel": "text-x-changelog",
    "programming.haskell": "applications-haskell",
    "programming.ide": "text-editor",
    "programming.java": "applications-java",
    "programming.python": "application-x-python-bytecode",
    "programming.tools": "gitg",
    "security": "preferences-system-firewall",
}
