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
from gi.repository import Gtk


class EopkgGroup(ProviderCategory):
    """ Wraps a GroupDB entry for top level groups """

    id = None
    group = None
    children = None

    def __init__(self, groupID, group):
        ProviderCategory.__init__(self)
        self.id = groupID
        self.group = group
        self.children = []

        # Just replace the icon on the fly with something that
        # fits better into the current theme
        settings = Gtk.Settings.get_default()
        icon_theme = settings.get_property("gtk-icon-theme-name")
        icon_theme = icon_theme.lower().replace("-", "")
        # Sneaky, I know.
        if icon_theme == "arcicons" or icon_theme == "arc":
            devIcon = "text-x-changelog"
        else:
            devIcon = "gnome-dev-computer"

        replacements = {
            "text-editor": "x-office-calendar",
            "redhat-programming": devIcon,
            "security-high": "preferences-system-privacy",
            "network": "preferences-system-network",
        }

        icon = str(self.group.icon)
        if icon in replacements:
            self.icon = replacements[icon]
        else:
            self.icon = icon

    def get_children(self):
        return self.children

    def get_name(self):
        return str(self.group.localName)

    def get_id(self):
        return str(self.id)

    def get_icon_name(self):
        """ Return internal eopkg group icon name """
        return self.icon
