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

from . import ProviderStorage, ProviderPlugin, ProviderItem
from . import PopulationFilter, ItemStatus
import pisi


class EopkgPlugin(ProviderPlugin):
    """ EopkgPlugin interfaces with the "native" package manager, i.e. eopkg """

    availDB = None
    installDB = None

    def __init__(self):
        self.availDB = pisi.db.packagedb.PackageDB()
        self.installDB = pisi.db.installdb.InstallDB()

    def populate_storage(self, storage, popfilter, extra):
        if popfilter == PopulationFilter.INSTALLED:
            return self.populate_installed(storage)
        elif popfilter == PopulationFilter.SEARCH:
            return self.populate_search(storage, extra)

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
            storage.add_item(pkg.get_id(), pkg)

    def populate_installed(self, storage):
        """ Populate from the installed filter """
        for pkgID in self.installDB.list_installed():
            pkgObject = self.installDB.get_package(pkgID)
            pkg = EopkgItem(pkgObject, pkgObject)
            storage.add_item(pkg.get_id(), pkg)


class EopkgItem(ProviderItem):
    """ EopkgItem abstracts access to the native package type, i.e. eopkg """

    installed = None
    available = None
    displayCandidate = None

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
        return "eopkg:{}".format(self.displayCandidate.name)

    def get_name(self):
        return self.displayCandidate.name

    def get_title(self):
        return self.displayCandidate.name

    def get_description():
        return self.displayCandidate.description

    def get_version(self):
        return self.displayCandidate.history[0].version
