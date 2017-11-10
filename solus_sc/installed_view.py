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

from gi.repository import Gtk, GLib
from .packages_view import ScPackagesView


class ScInstalledView(ScPackagesView):
    def handle_back(self):
        """ Go back to the main view """
        self.stack.set_visible_child_name("packages")
        self.owner.set_can_back(False)

    def can_back(self):
        """ Whether we can go back """
        return self.stack.get_visible_child_name() != "packages"

    def __init__(self, owner, basket, appsystem):
        ScPackagesView.__init__(self, owner, basket, appsystem)
        self.load_page.set_message(_("Solving the Paradox Of Choice"))

        self.stack.set_visible_child_name("loading")

    def init_view(self):
        model = self.get_model()
        model.set_sort_column_id(1, Gtk.SortType.ASCENDING)

        for pkg_name in self.basket.installdb.list_installed():
            pkg = self.basket.installdb.get_package(pkg_name)

            model.append(self.get_pkg_model(pkg))

        self.tview.set_model(model)
        GLib.idle_add(self.finish_view)
        return False

    def finish_view(self):
        self.load_page.spinner.stop()
        self.stack.set_visible_child_name("packages")
        return False

    def on_row_activated(self, tview, path, column, udata=None):
        """ User clicked a row, now try to load the page """
        pkg_name = self.get_pkg_name_from_path(tview, path)
        pkg = self.basket.installdb.get_package(pkg_name)
        self.details_view.update_from_package(pkg)
        self.stack.set_visible_child_name("details")
        self.owner.set_can_back(True)
