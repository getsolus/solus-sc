#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017-2020 Solus
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from ..base import ProviderSource

import os
import os.path


class FlatpakSource(ProviderSource):
    """ FlatpakSource provides an abstract wrapper for an underlying eopkg
        repository object so that it can be managed by the Software Center
    """

    active = None
    url = None
    name = None
    title = None

    remote = None  # Ref to the FlatpakRemote

    __gtype_name__ = "NxFlatpakSource"

    def get_name(self):
        # Breaking with convention but the title is always prettier.
        return self.title

    def __init__(self, remote):
        ProviderSource.__init__(self)
        self.remote = remote

        self.url = self.remote.get_url()
        self.name = self.remote.get_name()
        self.title = self.remote.get_title()

        self.active = not remote.get_disabled()

        # Compute appstream bits
        self.build_appstream_info()

    def build_appstream_info(self):
        """ Build the appstream paths for later """
        self.appstream_dir = self.remote.get_appstream_dir().get_path()
        print(self.appstream_dir)
        if os.path.exists(self.appstream_dir):
            for item in os.listdir(self.appstream_dir):
                if item.startswith("appstream.xml"):
                    self.appstream_file = os.path.join(
                        self.appstream_dir, item)
                    break
            self.appstream_icons = os.path.join(self.appstream_dir, "icons")
            return

        # Otherwise..
        self.appstream_file = os.path.join(
            self.appstream_dir, "appstream.xml.gz")
        self.appstream_icons = os.path.join(
            self.appstream_dir, "icons")

    def get_appstream_dir(self):
        """ Return appstream directory """
        return self.appstream_dir

    def get_appstream_file(self):
        """ Return appstream file path """
        return self.appstream_file

    def get_appstream_icons(self):
        """ Return icon path """
        return self.appstream_icons

    def describe(self):
        ret = "{} - {}".format(self.title, self.url)
        if not self.active:
            ret += " (inactive)"
        return ret

    def get_remote(self):
        """ Return the FlatpakRemote """
        return self.remote
