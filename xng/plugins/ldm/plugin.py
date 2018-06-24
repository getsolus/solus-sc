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

from ..base import ProviderPlugin

from gi.repository Ldm


class LdmPlugin(ProviderPlugin):
    """ LdmPlugin interacts with the other plugins so we can provide a dummy
        view to expose hardware drivers
    """

    __gtype_name__ = "NxLdmPlugin"
    cats = None

    def __init__(self):
        ProviderPlugin.__init__(self)
        self.build_categories()

    def build_categories(self):
        """ Find all of our possible categories and nest them. """
        self.cats = []

    def categories(self):
        return self.cats

    def populate_storage(self, storage, popfilter, extra):
        pass
