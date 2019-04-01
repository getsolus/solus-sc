#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017-2019 Solus
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import GObject
from xng.op_queue import OperationType
from ..util import sc_format_size_local
from collections import OrderedDict


class PopulationFilter:
    """ A population filter is provided to the provider plugin to begin
        population of a given type
    """

    INSTALLED = 0  # Installed packages
    SEARCH = 1     # Perform a search
    CATEGORY = 2   # List within category
    NEW = 3        # Find new packages
    RECENT = 4     # Find recently updated packages
    FEATURED = 5   # Basically "hot stuff"
    UPDATES = 6    # Only store updates in the list
    DRIVERS = 7    # Provide matching drivers to LDM plugin


class ItemStatus:
    """ The ItemStatus allows us to know the exact state of any given item
        as a combination of the various status flags
    """

    INSTALLED = 1 << 0
    UPDATE_NEEDED = 1 << 1      # We have an update available
    UPDATING = 1 << 2
    REMOVING = 1 << 3
    UPDATE_SECURITY = 1 << 4    # Security update available
    UPDATE_CRITICAL = 1 << 5    # Critical update available
    UPDATE_BUGFIX = 1 << 6      # Bugfix update available
    META_DEVEL = 1 << 7         # Is a development type of package
    META_CHANGELOG = 1 << 8     # Supports changelog functionality
    META_ESSENTIAL = 1 << 9     # Essential component. Do NOT remove!
    META_VIRTUAL = 1 << 10      # This is a fake item.
    META_THIRD_PARTY = 1 << 11  # Not officially supported


class ItemLink:
    """ The ItemLink enumeration allows us to define the relationship between
        different Items, i.e. why they're being added to an item in the first
        place.
    """

    PROVIDES = 1 << 0  # Sole provider of the requested functionality
    ENHANCES = 1 << 1  # Enhances the parent Item in some way.


class Transaction(GObject.Object):
    """ The Transaction class wraps a planned operation and returns the
        set of operations to be performed. This allows internal code to
        know the full set of operations to be completed ahead of time,
        including any automatic installs, conflict removals, etc.
    """

    __gtype_name__ = "NxTransaction"

    primary_item = None  # Associated primary item

    removals = None  # Any removals we need to perform (conflicts)

    installations = None  # Any installations to be performed

    upgrades = None  # Any upgrades to be performed

    op_type = None  # No initial operation type

    op_counter = None  # Top counter of all ops

    download_total = 0    # Total amount to download
    download_current = 0  # Total amount downloaded

    install_size = 0  # Total installation size
    remove_size = 0   # Total removal size

    autoremove = False  # Whether we autoremove or not

    items = None

    def __init__(self, primary_item=None):
        GObject.Object.__init__(self)

        self.primary_item = primary_item
        self.op_counter = 0
        if primary_item:
            self.plugin = primary_item.get_plugin()

        self.removals = set()
        self.installations = set()
        self.upgrades = set()
        self.items = dict()

    def set_autoremove(self, a):
        self.autoremove = a

    def get_plugin(self):
        return self.plugin

    def set_operation_type(self, op_type):
        """ Initiated by the context only """
        self.op_type = op_type

    def push_removal(self, item):
        """ Push a new removal operation """
        self.removals.add(item)
        self.op_counter += 1
        self.increment_remove_size(item)
        self.items[item.get_id()] = item

    def pop_removal(self, item):
        """ Pop a removal from the set of counted items """
        self.removals.remove(item)

    def push_installation(self, item):
        """ Push a new installation operation """
        self.installations.add(item)
        self.op_counter += 1
        self.increment_download_size(item)
        self.increment_install_size(item)
        self.items[item.get_id()] = item

    def pop_installation(self, item):
        """ When an item has completed, remove it """
        self.installations.remove(item)

    def push_reinstallation(self, item):
        """ Push a new reinstallation operation (remove + install) """
        self.removals.add(item)
        self.installations.add(item)
        self.op_counter += 2
        self.items[item.get_id()] = item
        self.increment_download_size(item)

    def push_upgrade(self, item):
        """ Push a new upgrade (explicit upgrade) operation """
        self.upgrades.add(item)
        self.op_counter += 1
        self.items[item.get_id()] = item
        self.increment_download_size(item)

    def pop_upgrade(self, item):
        """ Pop an upgrade from the set of counted upgrades """
        self.upgrades.remove(item)

    def increment_download_size(self, item):
        """ Add the total download size we're going to need """
        self.download_total += item.get_download_size()

    def increment_install_size(self, item):
        """ Add to the total install size """
        self.install_size += item.get_install_size()

    def increment_remove_size(self, item):
        """ Add to the total removal size """
        self.remove_size += item.get_install_size()

    def update_downloaded_size(self, size):
        """ Update the downloaded size with how much we've now got """
        self.download_current += size

    def count_operations(self):
        """ Total number of operations to be applied """
        return (self.count_installations() +
                self.count_removals() +
                self.count_upgrades())

    def get_fraction(self):
        """ Return the current fraction for all pending operations """
        return 1.0 - (float(self.count_operations()) / float(self.op_counter))

    def get_download_fraction(self):
        """ Return the total amount to be downloaded """
        if self.download_current == 0:
            return 1.0 / float(self.download_total)
        return float(self.download_current) / float(self.download_total)

    def count_installations(self):
        """ Total number of install operations """
        return len(self.installations)

    def count_removals(self):
        """ Total number of removal operations """
        return len(self.removals)

    def count_upgrades(self):
        """ Total number of upgrade operations """
        return len(self.upgrades)

    def describe(self):
        sb = None
        if self.op_type == OperationType.INSTALL:
            sb = "Install: {}".format(self.primary_item.get_id())
        elif self.op_type == OperationType.REMOVE:
            sb = "Remove: {}".format(self.primary_item.get_id())
        elif self.op_type == OperationType.UPGRADE:
            sb = "Upgrade: {}".format(self.primary_item.get_id())

        # Format for debug
        sb2 = sb
        sb2 += ", removals: {}, installs: {}, upgrades: {}".format(
            [x.get_id() for x in self.removals],
            [x.get_id() for x in self.installations],
            [x.get_id() for x in self.upgrades])
        print(sb2)

        return sb

    def get_install_size(self):
        """ Return string form of the total installation size """
        return sc_format_size_local(self.install_size)

    def get_removal_size(self):
        """ Return string form of the total removal size """
        return sc_format_size_local(self.remove_size)


class ProviderCategory(GObject.Object):
    """ ProviderCategory provides categorisation for the software center and
        allows nesting for the native items """

    __gtype_name__ = "NxProviderCategory"

    def __init__(self):
        GObject.Object.__init__(self)

    def get_id(self):
        """ Get the internal ID for this category """
        raise RuntimeError("implement get_id")

    def get_name(self):
        """ Get the display name for this category """
        raise RuntimeError("implement get_name")

    def get_icon_name(self):
        """ Get a display icon for this category """
        raise RuntimeError("implement get_icon_name")

    def get_children(self):
        """ Get any nested child categories """
        return []

    def get_software_label(self):
        """ Allow overriding the Software label in root-level categories """
        return None


class ProviderSource(GObject.Object):
    """ ProviderSource indicates sources used or available for use by a given
        plugin backend. In native implementations this is invariably a repo.
    """

    __gtype_name__ = "NxProviderSource"

    parent_plugin = None

    def __init__(self):
        GObject.Object.__init__(self)

    def get_name(self):
        """ Return human readable name for this source """
        raise RuntimeError("implement get_name")

    def describe(self):
        """ Request a human readable description for this source """
        raise RuntimeError("implement describe")

    def enable(self):
        """ Request this source be enabled """
        raise RuntimeError("implement enable")

    def disable(self):
        """ Request this source be disabled """
        raise RuntimeError("implement disable")

    def can_edit(self):
        """ Determines whether the source can be edited """
        return False

    def get_plugin(self):
        return self.parent_plugin


class ProviderStorage(GObject.Object):
    """ ProviderStorage is an abstract type that should be populated by
        existing plugins

        Storage may be recycled at any time and is used simply to allow
        dynamic "pushing" of items into the storage
    """

    __gtype_name__ = "NxProviderStorage"

    def __init__(self):
        GObject.Object.__init__(self)

    def add_item(self, id, item, popfilter):
        raise RuntimeError("implement add_item")

    def clear(self):
        raise RuntimeError("implement clear")


class SearchRequest(GObject.Object):
    """ SearchRequest is passed as the extra argument to populate_storage
        to permit controlling the search.
    """

    __gtype_name__ = "ScSearchRequest"

    installed_only = False
    term = None

    def __init__(self, term):
        GObject.Object.__init__(self)
        self.term = term

    def set_installed_only(self, installed_only):
        """ Whether this request is for installed only """
        self.installed_only = installed_only

    def get_installed_only(self):
        return self.installed_only

    def get_term(self):
        return self.term


class ProviderPlugin(GObject.Object):
    """ A ProviderPlugin provides its own managemenet and access to the
        underlying package management system to provide the options to the
        user
    """

    __gtype_name__ = "NxProviderPlugin"

    def __init__(self):
        GObject.Object.__init__(self)

    def get_name(self):
        raise RuntimeError("implement get_name")

    def populate_storage(self, storage, popfilter, extra):
        """ Populate storage using the given filter """
        raise RuntimeError("implement populate_storage")

    def cancel(self):
        """ Cancel any ongoing populare_storage calls """
        raise RuntimeError("implement cancel")

    def sources(self):
        """ Return the current set of sources for this plugin """
        return []

    def categories(self):
        """ Return the categories known by this plugin """
        return []

    def install_item(self, executor, transaction):
        raise RuntimeError("implement install_item")

    def remove_item(self, executor, transaction):
        raise RuntimeError("implement remove_item")

    def upgrade_item(self, executor, transaction):
        raise RuntimeError("implement upgrade_item")

    def plan_upgrade_item(self, items):
        """ Implementation must return a Transaction object for the given
            list of items to fully plan the given upgrade operation
        """
        raise RuntimeError("implement plan_upgrade_item")

    def plan_install_item(self, item):
        """ Implementation needs to return a Transaction object describing
            the operations required to satisfy the installation of this item
        """
        raise RuntimeError("implement plan_install_item")

    def plan_remove_item(self, item, automatic=False):
        """ Implementation needs to return a Transaction object describing
            the operations required to satisfy the removal of this item

            If `automatic` is set to True, the implementation should also
            plan to remove any automatically installed dependencies along
            with this
        """
        raise RuntimeError("implement plan_remove_item")

    def refresh_source(self, executor, source):
        """ Implementation needs to refresh the given source """
        raise RuntimeError("implement refresh_source")


class ProviderItem(GObject.Object):
    """ A ProviderItem is addded to the ProviderStorage by each ProviderPlugin
        and enables access + caching of various backend package management
        systems
    """

    status = None

    parent_plugin = None

    links = None

    def __init__(self):
        GObject.Object.__init__(self)
        # Default to no status
        self.status = 0
        self.links = OrderedDict()

    def push_link(self, reason, link):
        """ Link the item in the tree with the given reason """
        if reason not in self.links:
            self.links[reason] = set()
        self.links[reason].add(link)

    def pop_link(self, link):
        """ Remove the item from all link chains """
        for reason in self.links:
            if link in self.links[reason]:
                self.links[reason].remove(link)

    def get_status(self):
        """ Return the current status for this item """
        return self.status

    def remove_status(self, st):
        """ Remove a status field """
        self.status ^= st

    def add_status(self, st):
        """ Add a status field """
        self.status |= st

    def set_status(self, st):
        """ Set the complete status """
        self.status = st

    def has_status(self, st):
        return self.status & st == st

    def get_id(self):
        """ Every item should return their unique ID so that they can
            be tracked and differentiated between different backends
        """
        raise RuntimeError("implement get_id")

    def get_name(self):
        """ Actual name of the item. Title is stylised separateley """
        raise RuntimeError("implement get_name")

    def get_title(self):
        """ Each item should return an appropriate item for displaying
            as the stylised title
        """
        raise RuntimeError("implement get_title")

    def get_summary(self):
        """ Each item should return a brief summary suitable for single line
            listing of the summary beside the name/version/etc
        """
        raise RuntimeError("implement get_summary")

    def get_description(self):
        """ Each item should support returning their complete description
        """
        raise RuntimeError("implement get_description")

    def get_version(self):
        """ Each item should return a usable version string. This is purely
            for cosmectics
        """
        raise RuntimeError("implement get_version")

    def get_plugin(self):
        return self.parent_plugin

    def get_store(self):
        """ Plugins can use a different AsStore if required """
        return None

    def get_download_size(self):
        """ Return the total download size for the item """
        return 0

    def get_install_size(self):
        """ Return the total installation size for the item """
        return 0

    def get_icon_name(self):
        """ Return a custom icon name to bypass store requirements """
        return None

    def __str__(self):
        return self.get_id()
