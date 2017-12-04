#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk


class ScDetailsView(Gtk.Box):
    """ Shows details for a selected ProviderItem

        The details view is effectively the pretty view with all the relevant
        package/software details, screenshots, and actions to invoke removal,
        installation, etc.
    """

    context = None
    item = None

    __gtype_name__ = "ScDetailsView"

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.context = context
        self.show_all()

    def set_item(self, item):
        """ Update our UI for the current item """
        if item == self.item:
            return
        print("got updated")
