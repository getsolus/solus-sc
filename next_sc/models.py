#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk
import plugins
from plugins.base import ItemStatus

class ListingModel(Gtk.ListStore, plugins.base.ProviderStorage):
    """ ListingModel is used when listing packages in the view """

    skip_devel = False

    def __init__(self):
        Gtk.ListStore.__init__(self, str, str)

    def add_item(self, id, item):
        """ We'll just insert the item directly into the model """
        if self.skip_devel and item.has_status(ItemStatus.META_DEVEL):
            return
        self.append([item.get_title(), item.get_version()])


    def clear(self):
        """ Purge the list store """
        Gtk.ListStore.clear(self)
