#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk, GObject
import threading

from .loadpage import ScLoadingPage
from xng.plugins.base import PopulationFilter


class NotFoundPlaceholder(Gtk.Label):
    """ Found no search results. """

    label = None

    def __init__(self):
        Gtk.Label.__init__(self)

        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)
        # Unable to find any matching search results
        self.set_markup("<big>{}</big>".format(_("No results found")))
        self.set_use_markup(True)
        self.set_property("margin", 20)


class ScSearchView(Gtk.Box):
    """ Provide search functionality

        Simple threaded search results page
    """

    __gtype_name__ = "ScSearchView"

    context = None
    load = None
    listbox_results = None

    def get_page_name(self):
        return _("Search")

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.context = context

        # Main swap stack
        self.stack = Gtk.Stack.new()
        self.stack.set_homogeneous(False)
        self.stack.set_transition_type(
            Gtk.StackTransitionType.CROSSFADE)

        self.pack_start(self.stack, True, True, 0)

        # Hook up our load page
        self.load = ScLoadingPage()
        self.load.set_message(_("Concentrating really hard"))
        self.stack.add_named(self.load, 'loading')

        # Results page
        self.listbox_results = Gtk.ListBox.new()
        self.stack.add_named(self.listbox_results, 'results')
        holder = NotFoundPlaceholder()
        holder.show_all()
        self.listbox_results.set_placeholder(holder)

    def set_search_term(self, term):
        self.begin_busy()
        thr = threading.Thread(target=self.do_search, args=(term,))
        thr.daemon = True
        thr.start()

    def do_search(self, term):
        """ Begin performing the search in a threaded fashion """
        print("Searching for term: {}".format(term))

        # Kill existing results
        for child in self.listbox_results.get_children():
            child.destroy()

        for plugin in self.context.plugins:
            plugin.populate_storage(
                self,
                PopulationFilter.SEARCH,
                term)

        GObject.idle_add(self.end_busy)

    def begin_busy(self):
        """" We're about to start searching """
        self.context.set_window_busy(True)

    def end_busy(self):
        """ Move from the busy view now on idle thread-safe loop"""
        self.context.set_window_busy(False)
        self.stack.set_visible_child_name('results')
        return False

    def add_item(self, id, item, popfilter):
        """ Storage API """
        if popfilter != PopulationFilter.SEARCH:
            return
        self.add_search_result(item)

    def add_search_result(self, item):
        """ Add a new search result to the view """
        print(item.get_name())
