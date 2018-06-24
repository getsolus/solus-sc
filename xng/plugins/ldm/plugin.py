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

from ..base import ProviderPlugin, ProviderCategory, PopulationFilter

from gi.repository import Ldm

from .category import LdmRootCategory
from .item import LdmItem

class LdmPlugin(ProviderPlugin):
    """ LdmPlugin interacts with the other plugins so we can provide a dummy
        view to expose hardware drivers
    """

    __gtype_name__ = "NxLdmPlugin"
    cats = None

    manager = None

    def __init__(self):
        ProviderPlugin.__init__(self)
        self.cats = [LdmRootCategory()]

        # No hot plug events in the software center itself.
        self.manager = Ldm.Manager.new(Ldm.ManagerFlags.NO_MONITOR)
        self.manager.add_system_modalias_plugins()

    def categories(self):
        return self.cats

    def populate_storage(self, storage, popfilter, extra):
        if popfilter == PopulationFilter.CATEGORY:
            self.populate_category(storage, extra)
        pass

    def populate_category(self, storage, category):
        """ Populate categories """
        id = category.get_id()

        # Make sure its an LDM category first.
        if not id.startswith("ldm:"):
            return

        print("TODO: Populate category: {}".format(category.get_id()))

        # Build a list of devices for the selected category
        devices = self.manager.get_devices(category.ldm_type)
        for device in devices:
            item = LdmItem(device)
            id = item.get_id()
            storage.add_item(id, item, PopulationFilter.CATEGORY)
