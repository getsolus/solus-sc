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

from ..base import ProviderSource


class EopkgSource(ProviderSource):
    """ EopkgSource provides an abstract wrapper for an underlying eopkg
        repository object so that it can be managed by the Software Center
    """

    active = None
    url = None
    name = None
    plugin = None
    __gtype_name__ = "NxEopkgSource"

    def get_name(self):
        return self.name

    def __init__(self, rdb, repoName):
        ProviderSource.__init__(self)
        self.url = rdb.get_repo_url(repoName)
        self.name = repoName
        self.active = rdb.repo_active(repoName)

    def describe(self):
        # ret = "{} - {}".format(self.name, self.url)
        ret = self.name
        if not self.active:
            ret += " (inactive)"
        return ret
