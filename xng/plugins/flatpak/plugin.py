#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017-2020 Solus
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from ..base import ProviderPlugin, ProviderCategory, PopulationFilter

from gi.repository import Flatpak, GLib, Gio
from gi.repository import AppStreamGlib as As

# Plugin locals
from .item import FlatpakItem
from .source import FlatpakSource

import os


# 3 hours between appstream syncs
APPSTREAM_THRESHOLD_SECS = (60 * 60) * 3


class FlatpakRootCategory(ProviderCategory):
    """ Provider the root category for Flatpak navigation """

    sources = None
    components = None

    def __init__(self):
        ProviderCategory.__init__(self)

    def set_sources(self, sources):
        """ Update the sources """
        self.sources = sources

        self.components = list()
        for x in self.sources:
            # We only display remotes we can enumerate
            if x.remote.get_noenumerate():
                continue
            self.components.append(FlatpakComponent(x))

    def get_name(self):
        return _("Flatpak")

    def get_id(self):
        return "flatpak"

    def get_icon_name(self):
        # TODO: Only return this when icon theme supports it
        return "application-vnd.flatpak"

    def get_children(self):
        return self.components


class FlatpakComponent(ProviderCategory):
    """ Provides a category per remote """

    source = None

    def __init__(self, source):
        ProviderCategory.__init__(self)
        self.source = source

    def get_name(self):
        return self.source.get_name()

    def get_id(self):
        return "flatpak:{}".format(self.source.name)

    def get_icon_name(self):
        return "web-browser-symbolic"


class FlatpakPlugin(ProviderPlugin):
    """ FlatpakPlugin abstracts the underlying flatpak package management
        system in a fashion suitable for consumption by the Software Center
    """

    __gtype_name__ = "NxFlatpakPlugin"

    client = None  # FlatpakInstallation

    root_category = None  # To allow browsing flatpak

    remotes = None

    def __init__(self):
        ProviderPlugin.__init__(self)

        # We only manage the system-wide flatpak install, not user bits
        self.client = Flatpak.Installation.new_system(None)
        self.root_category = FlatpakRootCategory()

        # Our own temporary appstore..
        self.store = As.Store.new()

        # Cache the remotes because we actually need their appstream dirs
        self.build_remotes()

        # Pass the remotes to the root category
        self.root_category.set_sources(self.remotes)

    def get_name(self):
        return "flatpak"

    def build_remotes(self):
        """ Build our known remotes """
        self.remotes = []
        for remote in self.client.list_remotes(None):
            source = FlatpakSource(remote)
            source.parent_plugin = self
            self.remotes.append(source)

        self.build_appstream()

    def build_appstream(self):
        """ Update store with appstream information """
        for remote in self.remotes:
            appfile = remote.get_appstream_file()
            if not os.path.exists(appfile):
                continue
            # load_from_path seems broken right now
            gf = Gio.File.new_for_path(appfile)
            self.store.from_file(gf, remote.get_appstream_icons(), None)

    def sources(self):
        """ Return all flatpak sources """
        return self.remotes

    def refresh_source(self, executor, source):
        """ For flatpak we sync the remote ref *and* sync AppStream """
        self.executor = executor

        self.executor.set_progress_string(_("Updating repository information"))
        self.client.update_remote_sync(source.name, None)

        self.maybe_sync_appstream(executor, source)

    def maybe_sync_appstream(self, executor, source):
        """ Check if appstream data needs updating """

        # Do we need appstream data update?
        fremote = source.get_remote()
        modtime = 0
        try:
            updatefile = fremote.get_appstream_timestamp()
            finfo = updatefile.query_info("*", 0, None)
            modtime = finfo.get_modification_time().tv_sec
            print(modtime)
        except Exception as e:
            print(e)

        time_now = GLib.get_current_time()

        if time_now - modtime < APPSTREAM_THRESHOLD_SECS:
            print("AppStream data for {} is up to date".format(source.name))
            print(time_now - modtime)
            return

        self.executor.set_progress_string(_("Updating AppStream data"))
        self.client.update_appstream_sync(
            source.name,
            Flatpak.get_default_arch(),  # Use local architecture
            None)

        self.executor = None
        print("flatpak appstream synced")

    def categories(self):
        return [self.root_category]

    def populate_storage(self, storage, popfilter, extra):
        """ Dispatch the storage population to an appropriate helper """
        if popfilter == PopulationFilter.CATEGORY:
            self.populate_category(storage, extra)

    def populate_category(self, storage, category):
        """ Populate the storage with refs from the given category """
        if not category.get_id().startswith("flatpak:"):
            return
        remote_apps = self.client.list_remote_refs_sync(
            category.source.name,
            None)

        for remote_app in remote_apps:
            # Only want apps
            if not remote_app.get_kind() == Flatpak.RefKind.APP:
                continue
            # Only support native arch
            if remote_app.get_arch() != Flatpak.get_default_arch():
                continue
            item = self.build_item(remote_app)
            storage.add_item(item.get_id(), item, PopulationFilter.CATEGORY)

    def build_item(self, ref):
        """ Return an appropriate FlatpakItem for result sets """
        item = FlatpakItem(ref)
        item.store = self.store  # TODO: Construct one store per remote

        # TODO: Mimic eopkg and try to grab the avail/install difference
        return item
