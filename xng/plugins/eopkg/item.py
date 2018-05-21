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

from ..base import ProviderItem, ItemStatus
from pisi.operations.helper import calculate_download_sizes


class EopkgItem(ProviderItem):
    """ EopkgItem provides an abstract view of the underlying eopkg package
        object and exposes various control bits to integrate better within
        the Software Center

        Notably it attempts to track the difference between the installed
        package, if any, and the available repository package (again, if it
        exists).
    """

    installed = None
    available = None
    displayCandidate = None

    __gtype_name__ = "NxEopkgItem"

    def __init__(self, installed, available):
        ProviderItem.__init__(self)
        self.installed = installed
        self.available = available

        self.add_status(ItemStatus.META_CHANGELOG)

        if self.installed is not None:
            self.displayCandidate = self.installed
            self.add_status(ItemStatus.INSTALLED)
            relOld = self.installed.history[0].release
            relNew = relOld
            if self.available:
                relNew = self.available.history[0].release
            if relNew > relOld:
                self.add_status(ItemStatus.UPDATE_NEEDED)
        else:
            self.displayCandidate = self.available

        # Is this an essential item?
        if self.available and is_essential_package(self.available):
            self.add_status(ItemStatus.META_ESSENTIAL)

        name = self.get_name()
        if name.endswith("-dbginfo") or name.endswith("-devel"):
            self.add_status(ItemStatus.META_DEVEL)

    def get_id(self):
        return str(self.displayCandidate.name)

    def get_name(self):
        return self.displayCandidate.name

    def get_summary(self):
        return str(self.displayCandidate.summary)

    def get_title(self):
        return str(self.displayCandidate.name)

    def get_description(self):
        return str(self.displayCandidate.description)

    def get_version(self):
        return self.displayCandidate.history[0].version

    def get_download_size(self):
        return calculate_download_sizes((self.displayCandidate.name, ))[0]


# Mandatory components, removing will cause imminent death
essential_components = [
    "system.base",
]


# Essential packages, removing will upset and lead to imminent death.
essential_packages = [
    "mesalib",
    "xorg-server",
    "dhcpcd",
    "network-manager",
    "wpa_supplicant",
    "gvfs",
    "gnome-control-center",
    "solus-sc",
    "udisks",
    "upower",
]


def is_essential_package(pkg):
    """ Essential packages should NEVER be removed by the user. """
    if pkg.partOf in essential_components:
        return True
    if pkg.name in essential_packages:
        return True
    return False
