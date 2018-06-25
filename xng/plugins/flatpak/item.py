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

from ..base import ProviderItem, ItemStatus


class FlatpakItem(ProviderItem):
    """ FlatpakItem provides an abstract view of the underlying flatpak
        refs.
    """

    installed = None
    available = None
    displayCandidate = None
    store = None

    __gtype_name__ = "NxFlatpakItem"

    def __init__(self, available):
        ProviderItem.__init__(self)
        # Not officially supported by anyone
        self.add_status(ItemStatus.META_THIRD_PARTY)
        self.available = available
        self.displayCandidate = self.available

    def get_id(self):
        return self.displayCandidate.get_name()

    def get_name(self):
        return self.displayCandidate.get_name()

    def get_summary(self):
        return self.displayCandidate.format_ref()

    def get_title(self):
        return self.displayCandidate.get_name()

    def get_description(self):
        return self.displayCandidate.get_name()

    def get_version(self):
        return self.displayCandidate.get_commit()

    def get_store(self):
        return self.store
