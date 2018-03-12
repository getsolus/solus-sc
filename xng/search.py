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

from gi.repository import Gtk, GObject, Gdk, Pango
import threading

from .loadpage import ScLoadingPage
from xng.plugins.base import PopulationFilter, ItemStatus, ProviderItem


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


class ScSearchResult(Gtk.ListBoxRow):
    """ Display an item in a pretty view """

    __gtype_name__ = "ScSearchResult"

    item = None
    action_button = None

    def __init__(self, appsystem, item):
        Gtk.ListBoxRow.__init__(self)
        self.item = item
        item_id = item.get_id()

        main_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.add(main_box)

        # Pack the image first
        img = Gtk.Image.new()
        main_box.pack_start(img, False, False, 0)
        icon = appsystem.get_pixbuf_only(item_id)
        img.set_from_pixbuf(icon)

        stride_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        img.set_margin_end(12)
        main_box.pack_start(stride_box, True, True, 0)

        # Get the title
        name = appsystem.get_name(item_id, item.get_name())
        label = Gtk.Label(name)
        label.get_style_context().add_class("sc-bold")
        label.set_use_markup(True)
        label.set_margin_bottom(3)
        label.set_property("xalign", 0.0)
        label.set_halign(Gtk.Align.START)
        stride_box.pack_start(label, False, False, 0)

        # Get the summary
        summ = appsystem.get_summary(item_id, item.get_summary())
        summary = Gtk.Label(summ)
        summary.set_use_markup(True)
        summary.set_property("xalign", 0.0)
        summary.set_line_wrap(True)
        summary.set_line_wrap_mode(Pango.WrapMode.WORD)
        summary.set_halign(Gtk.Align.START)
        stride_box.pack_start(summary, False, False, 0)

        action_name = "Install"
        action_style = "suggested-action"
        if item.has_status(ItemStatus.INSTALLED):
            action_name = "Remove"
            action_style = "destructive-action"
        elif item.has_status(ItemStatus.UPDATE_NEEDED):
            action_name = "Update"

        self.action_button = Gtk.Button.new_with_label(action_name)
        self.action_button.set_halign(Gtk.Align.END)
        self.action_button.set_valign(Gtk.Align.CENTER)
        self.action_button.get_style_context().add_class(action_style)
        main_box.pack_end(self.action_button, False, False, 0)
        self.action_button.get_style_context().add_class("flat")

        self.get_style_context().add_class("search-item-row")


class ScSearchView(Gtk.Box):
    """ Provide search functionality

        Simple threaded search results page
    """

    __gtype_name__ = "ScSearchView"

    __gsignals__ = {
        'item-selected': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                          (ProviderItem,))
    }

    context = None
    load = None
    listbox_results = None
    holder = None

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
        self.listbox_results.set_activate_on_single_click(True)
        self.listbox_results.connect('row-activated', self.on_row_activated)

        self.stack.add_named(self.listbox_results, 'results')

        # Placeholder
        self.holder = NotFoundPlaceholder()
        self.holder.show_all()
        self.listbox_results.set_placeholder(self.holder)

    def on_row_activated(self, box, row, udata=None):
        """ Propogate item selection """
        if not row:
            return
        self.emit_selected_item(row.item)

    def emit_selected_item(self, item):
        """ Pass our item selection back up to the main window """
        self.emit('item-selected', item)

    def set_search_term(self, term):
        self.begin_busy()

        # Force UI to update itself before loading.
        while (Gtk.events_pending()):
            Gtk.main_iteration()

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
        self.holder.set_visible(False)
        self.stack.set_visible_child_name("loading")

    def end_busy(self):
        """ Move from the busy view now on idle thread-safe loop"""
        self.context.set_window_busy(False)
        self.stack.set_visible_child_name('results')
        self.holder.set_visible(True)
        return False

    def add_item(self, id, item, popfilter):
        """ Storage API """
        if popfilter != PopulationFilter.SEARCH:
            return
        self.add_search_result(item)

    def add_search_result(self, item):
        """ Add a new search result to the view """
        Gdk.threads_enter()

        wid = ScSearchResult(self.context.appsystem, item)
        wid.show_all()
        self.listbox_results.add(wid)

        Gdk.threads_leave()
