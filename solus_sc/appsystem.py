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

from gi.repository import AppStreamGlib as As
import os


class AppSystem:
    """ Mux calls into AppStream where appropriate
        TODO: Locale integration
    """

    store = None

    def __init__(self):
        self.store = As.Store()
        self.store.load(As.StoreLoadFlags.APP_INFO_SYSTEM)

    def get_summary(self, package):
        """ Return a usable summary for a package """
        app = self.store.get_app_by_pkgname(package.name)
        if not app:
            return package.summary
        return app.get_comment("C")

    def get_name(self, package):
        app = self.store.get_app_by_pkgname(package.name)
        if not app:
            return package.name
        return app.get_name("C")

    def get_icon(self, package):
        app = self.store.get_app_by_pkgname(package.name)
        if not app:
            if package.icon:
                return package.icon
            return "package-x-generic"
        icon = app.get_icon_default()
        if not icon:
            return
        fp = os.path.join(icon.get_prefix(), icon.get_name())
        return fp
        print icon.get_filename()
        print icon.get_prefix()
        return icon.get_name()
