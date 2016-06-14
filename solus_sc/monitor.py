#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#


from gi.repository import Gio


class ScMonitor:
    """ Background service that will always try and check for updates
        at a pre-configured frequency """

    net_monitor = None

    def __init__(self, app):
        self.net_monitor = Gio.NetworkMonitor.get_default()
        print("Network available? {}".format(
            self.net_monitor.get_network_available()))

    def check_for_updates(self):
        pass
