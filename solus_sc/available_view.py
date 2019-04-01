#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2019 Solus
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk
from .packages_view import ScPackagesView


class ScAvailableView(ScPackagesView):
    groups_view = None
    component = None

    def __init__(self, groups_view, owner):
        ScPackagesView.__init__(self, owner, owner.basket, owner.appsystem)
        self.load_page.set_message(_("Switching to the B-side of the cassette…"))
        self.groups_view = groups_view

    def on_row_activated(self, tview, path, column, udata=None):
        """ User clicked a row, now try to load the page """
        pkg_name = self.get_pkg_name_from_path(tview, path)

        pkg = self.basket.packagedb.get_package(pkg_name)
        self.groups_view.select_details(pkg)

    def set_component(self, component):
        if self.component and self.component == component:
            return
        self.component = component
        model = self.get_model()
        model.set_sort_column_id(1, Gtk.SortType.ASCENDING)

        packages = self.basket.componentdb.get_packages(component.name)

        # Take consideration
        if len(packages) >= 40:
            self.reset()

        for pkg_name in packages:
            pkg = self.basket.packagedb.get_package(pkg_name)

            model.append(self.get_pkg_model(pkg))

            while (Gtk.events_pending()):
                Gtk.main_iteration()

        self.tview.set_model(model)
        self.stack.set_visible_child_name("packages")
        self.load_page.spinner.stop()
