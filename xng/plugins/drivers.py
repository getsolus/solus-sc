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


from gi.repository import Ldm, GObject


class DriverManager(GObject.Object):
    """ Simple wrapper around Ldm

        We need this wrapper to make sure the Software Center can survive
        updates that alter LDM, such as the gi.require_version() call perhaps
        changing in future. So that the Software Center doesn't crash, we
        dynamically import at startup and just continue regardless.
    """

    __gtype_name__ = "DriverManager"
    manager = None

    def __init__(self):
        self.manager = Ldm.Manager.new(Ldm.ManagerFlags.NO_MONITOR)

    def reload(self):
        self.manager.add_system_modalias_plugins()
