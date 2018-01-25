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

from .appsystem import AppSystem
from .executor import Executor
from .util.fetcher import ScMediaFetcher
from gi.repository import GObject, GLib


class ScContext(GObject.Object):
    """ ScContext manages the global plugins and shared components """

    plugins = None
    appsystem = None
    has_loaded = False
    fetcher = None
    executor = None
    driver_manager = None

    __gtype_name__ = "ScContext"

    __gsignals__ = {
        'loaded': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
    }

    def __init__(self):
        GObject.Object.__init__(self)
        self.has_loaded = False

    def begin_load(self):
        """ Request a load for the system, i.e. after all components are
            now available for the UI """
        if self.has_loaded:
            return
        self.has_loaded = True
        self.init_ldm()
        self.init_plugins()
        self.fetcher = ScMediaFetcher()

        self.build_data()

    def init_ldm(self):
        """ Initialise Linux Driver Management if available. """
        try:
            from xng.plugins.drivers import DriverManager
            self.driver_manager = DriverManager()
        except Exception as e:
            print("LDM support unavailable on this system: {}".format(e))
            return
        self.driver_manager.reload()

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

    def emit_loaded(self):
        """ Emitted on the main thread to let the application know we're now
            ready and have available AppSystem data, etc. """
        print("defer loaded")
        self.emit('loaded')
        return False

    def build_data(self, args=None):
        """ Perform expensive operations """
        self.appsystem = AppSystem()
        self.executor = Executor()
        GLib.idle_add(self.emit_loaded)

    def begin_install(self, item):
        """ Begin the work necessary to install a package """
        packages = item.get_plugin().plan_install_item(item)
        names = [x.get_id() for x in packages]

        # TODO: Make sure this part is a dependency dialog
        print("begin_install: {}".format(", ".join(names)))

        # Now try the install
        item.get_plugin().install_item(packages)

    def begin_remove(self, item):
        """ Begin the work necessary to remove a package """
        packages = item.get_plugin().plan_remove_item(item)
        print("begin_remove: {}".format(packages))
