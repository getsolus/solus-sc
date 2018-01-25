#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

# Default server to talk to
ODRS_DEFAULT_SERVER = 'https://odrs.gnome.org/1.0/reviews/api'


class Context:
    """ Helper context for the ODRS API """

    cachedir = None
    server = None

    def __init__(self, cachedir, server=None):
        """ Construct a new context with default server """
        self.set_cachedir(cachedir)
        self.set_server(server)

    def set_server(self, server):
        """ Set the server used. If None, we'll use the default """
        if not server:
            self.server = ODRS_DEFAULT_SERVER
            return
        self.server = server

    def set_cachedir(self, cachedir):
        """ Set the cache dir, MUST exist! """
        if not cachedir:
            raise RuntimeError("missing cachedir, cannot continue")
        self.cachedir = cachedir
