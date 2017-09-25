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

from enum import Enum

class PopulationFilter(Enum):
    """ A population filter is provided to the provider plugin to begin
        population of a given type
    """

    INSTALLED = 0
    SEARCH = 1
    CATEGORY = 2

class ProviderStorage:
    """ ProviderStorage is an abstract type that should be populated by
        existing plugins

        Storage may be recycled at any time and is used simply to allow
        dynamic "pushing" of items into the storage
    """

    def add_item(self, id, item):
        raise RuntimeError("implement add_item")

    def clear(self):
        raise RuntimeError("implement clear")

class ProviderPlugin:
    """ A ProviderPlugin provides its own managemenet and access to the
        underlying package management system to provide the options to the
        user
    """

    def populate_storage(self, storage, popfilter, extra):
        """ Populate storage using the given filter """
        raise RuntimeError("implement populate_storage")

    def cancel(self):
        """ Cancel any ongoing populare_storage calls """
        raise RuntimeError("implement cancel")


class ProviderItem:
    """ A ProviderItem is addded to the ProviderStorage by each ProviderPlugin
        and enables access + caching of various backend package management
        systems
    """

    def get_id(self):
        """ Every item should return their unique ID so that they can
            be tracked and differentiated between different backends
        """
        raise RuntimeError("implement get_id")

    def get_title(self):
        """ Each item should return an appropriate item for displaying
            as the stylised title
        """
        raise RuntimeError("implement get_title")

    def get_description(self):
        """ Each item should support returning their complete description
        """
        raise RuntimeError("implement get_description")

    def get_version(self):
        """ Each item should return a usable version string. This is purely
            for cosmectics
        """
        raise RuntimeError("implement get_version")
