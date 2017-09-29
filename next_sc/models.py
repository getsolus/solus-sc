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

from gi.repository import Gtk, GdkPixbuf
import plugins
from plugins.base import ItemStatus, ProviderItem

class ListingModel(Gtk.ListStore, plugins.base.ProviderStorage):
    """ ListingModel is used when listing packages in the view """

    skip_devel = False
    appsystem = None

    def __init__(self, appsystem):
        Gtk.ListStore.__init__(self, str, GdkPixbuf.Pixbuf, str, ProviderItem)
        self.appsystem = appsystem
        # self.set_sort_column_id(2, Gtk.SortType.ASCENDING)

    def add_item(self, id, item, popfilter):
        """ We'll just insert the item directly into the model """
        if self.skip_devel and item.has_status(ItemStatus.META_DEVEL):
            return

        id = item.get_id()
        # Forcibly truncate summary. Nasty.
        summary = self.appsystem.get_summary(id, item.get_summary())
        if len(summary) > 76:
            summary = "%s…" % summary[0:76]

        name = self.appsystem.get_name(id, item.get_title())
        version = item.get_version()

        p_print = "<b>{}</b> - {}\n{}".format(name, version, summary)
        img = self.appsystem.get_pixbuf_only(id)
        self.append([p_print, img, name, item])

    def clear(self):
        """ Purge the list store """
        Gtk.ListStore.clear(self)
