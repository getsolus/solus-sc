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

from gi.repository import Flatpak, GLib

# Plugin locals
from .source import FlatpakSource

# 3 hours between appstream syncs
APPSTREAM_THRESHOLD_SECS = (60 * 60) * 3


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

    remotes = None

    def __init__(self):
        ProviderPlugin.__init__(self)

        # We only manage the system-wide flatpak install, not user bits
        self.client = Flatpak.Installation.new_system(None)
        self.root_category = FlatpakRootCategory()

        # Cache the remotes because we actually need their appstream dirs
        self.build_remotes()

        # Walk the remotes now
        for remote in self.remotes:
            fremote = remote.get_remote()
            appdir = fremote.get_appstream_dir()
            print appdir.get_path()

    def build_remotes(self):
        """ Build our known remotes """
        self.remotes = []
        for remote in self.client.list_remotes(None):
            source = FlatpakSource(remote)
            source.parent_plugin = self
            self.remotes.append(source)

    def populate_storage(self, storage, popfilter, extra):
        print("flatpak: not yet implemented =)")

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
        appdir = fremote.get_appstream_dir()
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
