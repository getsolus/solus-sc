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

from ..base import ProviderPlugin, ProviderCategory

from gi.repository import Ldm

class LdmRootCategory(ProviderCategory):

    __gtype_name__ = "NxLdmRootCategory"

    def __init__(self):
        ProviderCategory.__init__(self)

    def get_icon_name(self):
        return "cs-cat-hardware"

    def get_id(self):
        return "ldm-category"

    def get_name(self):
        return _("Hardware & Drivers")

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
        pass
