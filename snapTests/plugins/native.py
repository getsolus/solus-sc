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

from . import ProviderStorage, ProviderPlugin, ProviderItem, PopulationFilter
import pisi


class NativePlugin(ProviderPlugin):
    """ NativePlugin interfaces with the "native" package manager, i.e. eopkg """

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
        return

    def populate_installed(self, storage):
        """ Populate from the installed filter """
        for pkgID in self.installDB.list_installed():
            pkgObject = self.installDB.get_package(pkgID)
            pkg = NativeItem(pkgObject)
            storage.add_item(pkg.get_id(), pkg)


class NativeItem(ProviderItem):
    """ NativeItem abstracts access to the native package type, i.e. eopkg """

    pkg = None

    def __init__(self, pkg):
        ProviderItem.__init__(self)
        self.pkg = pkg

    def get_id(self):
        return "native:{}".format(self.pkg.name)

    def get_name(self):
        return self.pkg.name

    def get_title(self):
        return self.pkg.name

    def get_description():
        return self.pkg.description

    def get_version(self):
        return self.pkg.history[0].version
