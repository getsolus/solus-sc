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

from ..base import ProviderPlugin, ProviderCategory

from gi.repository import Flatpak

# Plugin locals
from .source import FlatpakSource


class FlatpakRootCategory(ProviderCategory):
    """ Provider the root category for Flatpak navigation """

    def __init__(self):
        ProviderCategory.__init__(self)

    def get_name(self):
        return _("Flatpak")

    def get_id(self):
        return "flatpak"

    def get_icon_name(self):
        # TODO: Only return this when icon theme supports it
        return "application-vnd.flatpak"


class FlatpakPlugin(ProviderPlugin):
    """ FlatpakPlugin abstracts the underlying flatpak package management
        system in a fashion suitable for consumption by the Software Center
    """

    __gtype_name__ = "NxFlatpakPlugin"

    client = None  # FlatpakInstallation

    root_category = None  # To allow browsing flatpak

    def __init__(self):
        ProviderPlugin.__init__(self)

        # We only manage the system-wide flatpak install, not user bits
        self.client = Flatpak.Installation.new_system(None)
        self.root_category = FlatpakRootCategory()

    def populate_storage(self, storage, popfilter, extra):
        print("flatpak: not yet implemented =)")

    def sources(self):
        """ Return all flatpak sources """
        sources = []
        for remote in self.client.list_remotes(None):
            source = FlatpakSource(remote)
            source.parent_plugin = self
            sources.append(source)
        return sources

    def refresh_source(self, executor, source):
        print("flatpak refresh source: {}".format(source.get_name()))
        self.client.update_remote_sync(source.name, None)
        print("flatpak source refreshed, begin appstream sync")
        self.client.update_appstream_sync(
            source.name,
            Flatpak.get_default_arch(),  # Use local architecture
            None)
        print("flatpak appstream synced")

    def categories(self):
        return [self.root_category]
