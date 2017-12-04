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

from .appsystem import AppSystem
from gi.repository import GObject
import threading


class ScContext(GObject.Object):
    """ ScContext manages the global plugins and shared components """

    plugins = None
    appsystem = None

    __gtype_name__ = "ScContext"

    def __init__(self):
        GObject.Object.__init__(self)
        self.init_plugins()

        # Lazy load now
        thr = threading.Thread(target=self.build_data)
        thr.daemon = True
        thr.start()

    def init_plugins(self):
        """ Take care of setting up our plugins
            This takes special care to wrap the initial import in case we
            have a module level import that would fail, i.e. import of
            the snapd-glib binding
        """
        self.plugins = []
        snap = None
        osPlugin = None
        try:
            from xng.plugins.snapd import SnapdPlugin
            snap = SnapdPlugin()
        except Exception as e:
            print("snapd support unavailable on this system: {}".format(e))
            snap = None

        if snap is not None:
            self.plugins.append(snap)

        try:
            from xng.plugins.native import get_native_plugin
            osPlugin = get_native_plugin()
        except Exception as e:
            print("Native plugin support unavailable for this system: {}".
                  format(e))
        if osPlugin is not None:
            self.plugins.insert(0, osPlugin)
        else:
            print("WARNING: Unsupported OS, native packaging unavailable!")

    def build_data(self, args=None):
        """ Perform expensive operations """
        self.appsystem = AppSystem()
        print("defer loaded")
