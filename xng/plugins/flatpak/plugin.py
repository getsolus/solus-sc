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

from ..base import ProviderPlugin

from gi.repository import Flatpak


class FlatpakPlugin(ProviderPlugin):
    """ FlatpakPlugin abstracts the underlying flatpak package management
        system in a fashion suitable for consumption by the Software Center
    """

    __gtype_name__ = "NxFlatpakPlugin"

    client = None  # FlatpakInstallation

    def __init__(self):
        ProviderPlugin.__init__(self)

        # We only manage the system-wide flatpak install, not user bits
        self.client = Flatpak.Installation.new_system(None)

        for remote in self.client.list_remotes(None):
            print(" > flatpak remote: {} {}".format(
                remote.get_title(), remote.get_url()))

    def populate_storage(self, storage, popfilter, extra):
        print("flatpak: not yet implemented =)")
