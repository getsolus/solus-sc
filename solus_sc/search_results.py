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

from gi.repository import Gtk
import difflib
from .util import is_package_debug
from .packages_view import ScPackagesView


class BlankPage(Gtk.VBox):
    """ Simple placeholder page, nothing fancy. """

    label = None

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)
        # Search page, prompt to begin searching
        self.label = Gtk.Label("<big>{}</big>".format(
            _("Type a query to get started")))
        self.label.set_use_markup(True)

        self.pack_start(self.label, False, False, 0)
        self.label.set_property("margin", 20)


class NotFoundPage(Gtk.VBox):
    """ Found no search results. """

    label = None

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)
        # Unable to find any matching search results
        self.label = Gtk.Label("<big>{}</big>".format(
            _("No results found")))
        self.label.set_use_markup(True)

        self.pack_start(self.label, False, False, 0)
        self.label.set_property("margin", 20)


class ScSearchResults(ScPackagesView):
    empty_page = None
    notfound_page = None
    search_page = None

    def __init__(self, search_page, owner):
        ScPackagesView.__init__(self, owner, owner.basket, owner.appsystem)
        self.load_page.set_message(_("Concentrating really hard"))

        self.search_page = search_page

        # Not found/ search for somethin pls
        self.empty_page = BlankPage()
        self.empty_page.show()
        self.stack.add_named(self.empty_page, "empty")

        # not found
        self.notfound_page = NotFoundPage()
        self.stack.add_named(self.notfound_page, "not-found")

        self.stack.set_visible_child_name("empty")

    def on_row_activated(self, tview, path, column, udata=None):
        """ User clicked a row, now try to load the page """
        pkg_name = self.get_pkg_name_from_path(tview, path)

        if self.basket.packagedb.has_package(pkg_name):
            pkg = self.basket.packagedb.get_package(pkg_name)
        else:
            pkg = self.basket.installdb.get_package(pkg_name)
        self.search_page.select_details(pkg)

    def set_search_term(self, term):
        if term.strip() == "":
            return
        model = self.get_model()

        self.reset()

        # Make sure spaces work and match potential packages
        term = term.replace(" ", "[-_ ]")

        try:
            srslt = set(self.basket.packagedb.search_package([term]))
            srslt.update(self.basket.installdb.search_package([term]))
        except Exception as e:
            # Invalid regex, basically, from someone smashing FIREFOX????
            print(e)
            self.stack.set_visible_child_name("not-found")
            self.load_page.spinner.stop()
            return

        leaders = difflib.get_close_matches(term.lower(),
                                            srslt, cutoff=0.5)
        packages = leaders
        packages.extend(sorted([x for x in srslt if x not in leaders]))
        added = False
        for pkg_name in packages:
            if self.basket.packagedb.has_package(pkg_name):
                pkg = self.basket.packagedb.get_package(pkg_name)
            else:
                pkg = self.basket.installdb.get_package(pkg_name)

            # Always hide debug packages
            if is_package_debug(pkg) and "dbg" not in term:
                continue

            added = True

            model.append(self.get_pkg_model(pkg))

            while (Gtk.events_pending()):
                Gtk.main_iteration()

        if not added:
            self.stack.set_visible_child_name("not-found")
        else:
            self.stack.set_visible_child_name("packages")

        self.tview.set_model(model)
        self.load_page.spinner.stop()

    def clear_view(self):
        self.tview.set_model(None)
        self.stack.set_visible_child_name("empty")
        self.queue_draw()
