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

from .base import ProviderPlugin, ProviderItem, ProviderSource
from .base import PopulationFilter, ItemStatus
import pisi


class EopkgSource(ProviderSource):
    """ EopkgSource wraps a repository object """

    active = None
    url = None
    name = None

    __gtype_name__ = "NxEopkgSource"

    def __init__(self, rdb, repoName):
        ProviderSource.__init__(self)
        self.url = rdb.get_repo_url(repoName)
        self.name = repoName
        self.active = rdb.repo_active(repoName)

    def describe(self):
        ret = "{} - {}".format(self.name, self.url)
        if not self.active:
            ret += " (inactive)"
        return ret


class EopkgPlugin(ProviderPlugin):
    """ EopkgPlugin interfaces with the eopkg package manager """

    availDB = None
    installDB = None

    repos = None

    __gtype_name__ = "NxEopkgPlugin"

    def __init__(self):
        ProviderPlugin.__init__(self)
        self.availDB = pisi.db.packagedb.PackageDB()
        self.installDB = pisi.db.installdb.InstallDB()
        self.repoDB = pisi.db.repodb.RepoDB()

    def sources(self):
        repos = []
        mainRepos = self.repoDB.list_repos(only_active=False)
        for x in mainRepos:
            repos.append(EopkgSource(self.repoDB, x))
        return repos

    def populate_storage(self, storage, popfilter, extra):
        if popfilter == PopulationFilter.INSTALLED:
            return self.populate_installed(storage)
        elif popfilter == PopulationFilter.SEARCH:
            return self.populate_search(storage, extra)
        elif popfilter == PopulationFilter.RECENT:
            return self.populate_recent(storage, extra)
        elif popfilter == PopulationFilter.NEW:
            return self.populate_new(storage, extra)

    def populate_recent(self, storage, appsystem):
        """ Populate home view with recently updated packages """

        # Hack for demo
        recents = [
            "gnome-weather",
            "gnome-mpv",
            "kdenlive",
            "hexchat",
            "dustrac",
        ]

        for i in recents:
            pkg = self.availDB.get_package(i)
            item = EopkgItem(None, pkg)
            storage.add_item(item.get_id(), item, PopulationFilter.RECENT)

    def populate_new(self, storage, appsystem):
        """ Populate home view with recently uploaded packages """

        # Hack for demo
        news = [
            "lutris",
            "darktable",
            "shotwell",
            "gnome-music",
            "gnome-maps",
        ]

        for i in news:
            pkg = self.availDB.get_package(i)
            item = EopkgItem(None, pkg)
            storage.add_item(item.get_id(), item, PopulationFilter.NEW)

    def populate_search(self, storage, term):
        """ Attempt to search for a given term in the DB """
        # Trick eopkg into searching through spaces and hyphens
        term = term.replace(" ", "[-_ ]")

        try:
            srslt = set(self.availDB.search_package([term]))
            srslt.update(self.installDB.search_package([term]))
        except Exception as e:
            # Invalid regex, basically, from someone smashing FIREFOX????
            print(e)
            return

        for item in srslt:
            available = None
            installed = None

            if self.installDB.has_package(item):
                installed = self.installDB.get_package(item)
            if self.availDB.has_package(item):
                available = self.availDB.get_package(item)

            pkg = EopkgItem(installed, available)
            storage.add_item(pkg.get_id(), pkg, PopulationFilter.SEARCH)

    def populate_installed(self, storage):
        """ Populate from the installed filter """
        for pkgID in self.installDB.list_installed():
            pkgObject = self.installDB.get_package(pkgID)
            pkg = EopkgItem(pkgObject, pkgObject)
            storage.add_item(pkg.get_id(), pkg, PopulationFilter.INSTALLED)


class EopkgItem(ProviderItem):
    """ EopkgItem abstracts access to the native package type, i.e. eopkg """

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
        else:
            self.displayCandidate = self.available

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
