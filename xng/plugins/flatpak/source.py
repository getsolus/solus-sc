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

from ..base import ProviderSource


class FlatpakSource(ProviderSource):
    """ FlatpakSource provides an abstract wrapper for an underlying eopkg
        repository object so that it can be managed by the Software Center
    """

    active = None
    url = None
    name = None
    title = None

    __gtype_name__ = "NxFlatpakSource"

    def get_name(self):
        # Breaking with convention but the title is always prettier.
        return self.title

    def __init__(self, remote):
        ProviderSource.__init__(self)

        self.url = remote.get_url()
        self.name = remote.get_name()
        self.title = remote.get_title()

        self.active = not remote.get_disabled()

    def describe(self):
        ret = "{} - {}".format(self.title, self.url)
        if not self.active:
            ret += " (inactive)"
        return ret
