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

from .base import ProviderPlugin, ProviderItem, ProviderSource, \
    ProviderCategory
from .base import PopulationFilter, ItemStatus
from gi.repository import AppStreamGlib as As
import pisi
from pisi.operations.install import plan_install_pkg_names
import time


def find_have_data(adb, store):
    """ Find all packages with AppStream data """
    ret = []

    for key in adb.list_packages(None):
        app = store.get_app_by_pkgname(key)
        if not app:
            continue
        # Only want desktop apps here
        if app.get_kind() != As.AppKind.DESKTOP:
            continue
        ret.append(key)
    return ret


def filter_packages_by_data(adb, store):
    """ Return available packages by appdata only """
    pkgs = find_have_data(adb, store)
    ret = []
    for item in pkgs:
        pkg = adb.get_package(item)
        ret.append(pkg)
    return ret


def unmangle_date(tstamp):
    try:
        ret = time.strptime(tstamp, "%Y-%m-%d")
        return ret
    except Exception:
        # Probably because old eopkg pspec
        pass
    try:
        ret = time.strptime(tstamp, "%m-%d-%Y")
        return ret
    except:
        return 0


def history_sort(pkgA, pkgB):
    dateA = pkgA.history[0].date
    dateB = pkgB.history[0].date
    aa = unmangle_date(dateA)
    ab = unmangle_date(dateB)

    return cmp(aa, ab)


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
]


def is_essential_package(pkg):
    """ Essential packages should NEVER be removed by the user. """
    if pkg.partOf in essential_components:
        return True
    if pkg.name in essential_packages:
        return True
    return False


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

    def get_children(self):
        return self.children

    def get_name(self):
        return str(self.group.localName)

    def get_id(self):
        return str(self.id)

    def get_icon_name(self):
        """ Return internal eopkg group icon name """
        return str(self.group.icon)


class EopkgComponent(ProviderCategory):
    """ Wraps an eopkg component """

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
        return "package-x-generic"


class EopkgPlugin(ProviderPlugin):
    """ EopkgPlugin interfaces with the eopkg package manager """

    availDB = None
    installDB = None
    groupDB = None
    compDB = None
    cats = None

    repos = None

    __gtype_name__ = "NxEopkgPlugin"

    def __init__(self):
        ProviderPlugin.__init__(self)
        self.availDB = pisi.db.packagedb.PackageDB()
        self.installDB = pisi.db.installdb.InstallDB()
        self.repoDB = pisi.db.repodb.RepoDB()
        self.groupDB = pisi.db.groupdb.GroupDB()
        self.compDB = pisi.db.componentdb.ComponentDB()

        self.build_categories()

    def build_categories(self):
        """ Find all of our possible categories and nest them. """
        self.cats = []
        groups = self.groupDB.list_groups()
        groups.sort()
        for groupID in groups:
            group = self.groupDB.get_group(groupID)
            item = EopkgGroup(groupID, group)

            components = self.groupDB.get_group_components(groupID)
            components.sort()

            for compID in components:
                comp = self.compDB.get_component(compID)
                childItem = EopkgComponent(compID, comp)
                item.children.append(childItem)

            self.cats.append(item)

    def categories(self):
        return self.cats

    def sources(self):
        repos = []
        mainRepos = self.repoDB.list_repos(only_active=False)
        for x in mainRepos:
            repos.append(EopkgSource(self.repoDB, x))
        return repos

    def populate_storage(self, storage, popfilter, extra, cancel):
        if popfilter == PopulationFilter.INSTALLED:
            return self.populate_installed(storage)
        elif popfilter == PopulationFilter.SEARCH:
            return self.populate_search(storage, extra, cancel)
        elif popfilter == PopulationFilter.RECENT:
            return self.populate_recent(storage, extra)
        elif popfilter == PopulationFilter.NEW:
            return self.populate_new(storage, extra)
        elif popfilter == PopulationFilter.FEATURED:
            return self.populate_featured(storage, extra)

    def populate_recent(self, storage, appsystem):
        """ Populate home view with recently updated packages """

        limit = 20  # Arbitrary right now

        inp = filter_packages_by_data(self.availDB, appsystem.store)
        inp.sort(history_sort, reverse=True)
        if len(inp) > limit:
            inp = inp[0:limit]

        for pkg in inp:
            ppkg = None
            if self.installDB.has_package(pkg.name):
                ppkg = self.installDB.get_package(pkg.name)
            item = EopkgItem(ppkg, pkg)
            item.parent_plugin = self
            storage.add_item(item.get_id(), item, PopulationFilter.RECENT)

    def populate_new(self, storage, appsystem):
        """ Populate home view with recently uploaded packages """

        # Hack for demo
        news = [
            "gnome-weather",
            "gnome-mpv",
            "kdenlive",
            "hexchat",
            "dustrac",
        ]

        for i in news:
            pkg = self.availDB.get_package(i)
            ppkg = None
            if self.installDB.has_package(i):
                ppkg = self.installDB.get_package(i)
            item = EopkgItem(ppkg, pkg)
            item.parent_plugin = self
            storage.add_item(item.get_id(), item, PopulationFilter.NEW)

    def populate_featured(self, storage, appsystem):
        """ Populate home view with "hot" packages """

        # Hack for demo
        news = [
            "sayonara-player",
            "pitivi",
            "libreoffice-writer",
            "kdeconnect",
            "polari",
            "tilix",
            "inkscape",
            "gnome-boxes",
        ]

        for i in news:
            pkg = self.availDB.get_package(i)
            ppkg = None
            if self.installDB.has_package(i):
                ppkg = self.installDB.get_package(i)
            item = EopkgItem(ppkg, pkg)
            item.parent_plugin = self
            storage.add_item(item.get_id(), item, PopulationFilter.NEW)

    def populate_search(self, storage, term, cancel):
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

            # Check on each item if we need to bail NOW
            if cancel.is_set():
                print("Cancelled?!?")
                return

            if self.installDB.has_package(item):
                installed = self.installDB.get_package(item)
            if self.availDB.has_package(item):
                available = self.availDB.get_package(item)

            pkg = EopkgItem(installed, available)
            pkg.parent_plugin = self
            storage.add_item(pkg.get_id(), pkg, PopulationFilter.SEARCH)
        print("eopkg done!")

    def populate_installed(self, storage):
        """ Populate from the installed filter """
        for pkgID in self.installDB.list_installed():
            pkgObject = self.installDB.get_package(pkgID)
            pkg = EopkgItem(pkgObject, pkgObject)
            pkg.parent_plugin = self
            storage.add_item(pkg.get_id(), pkg, PopulationFilter.INSTALLED)

    def build_item(self, name):
        """ Build a complete item definition """
        avail = None
        installed = None
        if self.availDB.has_package(name):
            avail = self.availDB.get_package(name)
        if self.installDB.has_package(name):
            installed = self.installDB.get_package(name)
        item = EopkgItem(installed, avail)
        item.parent_plugin = self
        return item

    def plan_install_item(self, item):
        """ Plan the installation of a given item """
        (pg, pkgs) = plan_install_pkg_names([item.get_id()])
        # We only want the package set, not the graph
        ret = []
        for name in pkgs:
            ret.append(self.build_item(name))
        return ret


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
            self.add_status(ItemStatus.INSTALLED)
            relNew = self.available.history[0].release
            relOld = self.installed.history[0].release
            if relNew > relOld:
                self.add_status(ItemStatus.UPDATE_NEEDED)
        else:
            self.displayCandidate = self.available

        # Is this an essential item?
        if is_essential_package(self.available):
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
