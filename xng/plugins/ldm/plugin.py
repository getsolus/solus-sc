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
from ..base import ItemLink

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
    context = None  # Back reference to the owning context, special case

    temporary_drivers = None  # Quick list for add_item storage API

    def __init__(self, context):
        ProviderPlugin.__init__(self)
        self.context = context
        self.cats = [LdmRootCategory()]

        # No hot plug events in the software center itself.
        self.manager = Ldm.Manager.new(Ldm.ManagerFlags.NO_MONITOR)
        self.manager.add_system_modalias_plugins()

    def get_name(self):
        return "ldm"

    def categories(self):
        return self.cats

    def populate_storage(self, storage, popfilter, extra):
        if popfilter == PopulationFilter.CATEGORY:
            self.populate_category(storage, extra)
        elif popfilter == PopulationFilter.DRIVERS:
            raise RuntimeError("fatal recursion!")

    def populate_category(self, storage, category):
        """ Populate categories """
        id = category.get_id()

        # Make sure its an LDM category first.
        if not id.startswith("ldm:"):
            return

        items = []

        # Build a list of devices for the selected category
        devices = self.manager.get_devices(category.ldm_type)
        for device in devices:
            item = LdmItem(device)
            id = item.get_id()
            self.assign_providers(item)
            items.append(item)

        # Pre-sort for display
        items.sort(self.device_sort, reverse=True)

        for item in items:
            storage.add_item(id, item, PopulationFilter.CATEGORY)

    def device_sort(self, devA, devB):
        return cmp(devA.get_name().lower(), devB.get_name().lower())

    def assign_providers(self, item):
        """ Attempt to relate and assign any relevant providers for a device
            by querying the foreign providers from other plugins if possible
        """
        providers = self.manager.get_providers(item.device)
        if not providers:
            return
        for provider in providers:
            print("Provider: {}".format(provider))

            # Push all of these providers to the current ProviderItem
            for foreigner in self.get_foreign_items(provider):
                item.push_link(ItemLink.PROVIDER, foreigner)

    def get_foreign_items(self, provider):
        """ Query all plugins to find the true providers of an LdmProvider """
        package_name = provider.get_package()
        self.temporary_drivers = []
        for plugin in self.context.plugins:
            if plugin == self:
                continue
            print("Asking {} for providers of {}".format(
                plugin,  package_name))
            plugin.populate_storage(self, PopulationFilter.DRIVERS, provider)
        return self.temporary_drivers

    def add_item(self, id, item, popfilter):
        """ Handle crosstalk from foreign plugins """
        if popfilter != PopulationFilter.DRIVERS:
            raise RuntimeError("fatal use of API!")

        print("Adding driver: {}".format(id))
        self.temporary_drivers.append(item)
