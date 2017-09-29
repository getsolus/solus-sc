#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from .base import ProviderPlugin, ProviderItem, PopulationFilter, ProviderCategory
from gi.repository import Snapd as snapd

class SnapdCategory(ProviderCategory):

    __gtype_name__ = "NxSnapdCategory"

    def __init__(self):
        ProviderCategory.__init__(self)

    def get_icon_name(self):
        return "start-here-ubuntu"

    def get_id(self):
        return "ubuntu-rally"

    def get_name(self):
        return "Ubuntu Rally Demo"


class SnapdPlugin(ProviderPlugin):
    """ SnapdPlugin provides backend support to solus-sc to interact with the
        snapd daemon via snapd-glib bindings. """

    __gtype_name__ = "NxSnapdPlugin"

    snapd_client = None

    # Cache the snap items by their internal ID
    items = None

    def __init__(self):
        ProviderPlugin.__init__(self)
        self.items = dict()
        # Ensure communication with snapd daemon
        self.snapd_client = snapd.Client()
        self.snapd_client.connect_sync()
        self.snapd_client.get_system_information_sync()

        self.children = []
        self.children.append(SnapdCategory())

    def categories(self):
        return self.children

    def populate_storage(self, storage, popfilter, extra):
        if popfilter == PopulationFilter.INSTALLED:
            return self.populate_installed(storage)
        elif popfilter == PopulationFilter.SEARCH:
            return self.populate_search(storage, extra)
        elif popfilter == PopulationFilter.CATEGORY:
            return self.populate_category(storage, extra)

    def populate_category(self, storage, extra):
        snaps = [
            "ohmygiraffe",
            "emoj",
            "http",
            "gnome-calculator",
            "vlc",
        ]
        for i in snaps:
            rm = self.snapd_client.find_sync(snapd.FindFlags.MATCH_NAME, i)[0]
            snap = SnapdItem(rm)
            snap_id = snap.get_id()
            storage.add_item(snap_id, snap, PopulationFilter.CATEGORY)

    def populate_search(self, storage, term):
        """ Search for the remote snap """
        # TODO: Make async.
        listage = self.snapd_client.find_sync(snapd.FindFlags.NONE, term)
        if listage is None or len(listage) < 1:
            return
        for i in listage:
            # TODO: Cache??
            snap = SnapdItem(i)
            snap_id = snap.get_id()
            storage.add_item(snap_id, snap, PopulationFilter.SEARCH)

    def populate_installed(self, storage):
        for snap in self.snapd_client.list_sync():
            snap_id = "snapd:{}".format(snap.get_id())
            if snap_id in self.items:
                snap = self.items[snap_id]
                storage.add_item(snap_id, snap, PopulationFilter.INSTALLED)
                continue
            snap = SnapdItem(snap)
            storage.add_item(snap_id, snap, PopulationFilter.INSTALLED)
            self.push_item(snap)

    def push_item(self, snap):
        """ Hold a reference to the item to speed things up """
        self.items[snap.get_id()] = snap


class SnapdItem(ProviderItem):
    """ A SnapdItem is a reference to either a remote or local snapd.Snap """

    __gtype_name__ = "NxSnapdItem"

    snap = None
    enhanced_source = None

    def __init__(self, snap):
        ProviderItem.__init__(self)
        self.snap = snap

    def get_id(self):
        return "snapd:{}".format(self.snap.get_id())

    def get_name(self):
        return self.snap.get_name()

    def get_summary(self):
        return self.snap.get_summary()

    def get_title(self):
        return self.snap.get_title()

    def get_description(self):
        return self.snap.get_description()

    def get_version(self):
        return "{}-rev{}".format(
            self.snap.get_version(),
            self.snap.get_revision(),
        )
