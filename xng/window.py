#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk, GObject
from .context import ScContext
from .home import ScHomeView
from .details import ScDetailsView


class ScMainWindow(Gtk.ApplicationWindow):

    # Headerbar
    hbar = None
    search_button = None
    back_button = None

    # Search bits
    search_revealer = None
    search_bar = None
    search_entry = None

    mode_open = None

    # Tracking
    context = None
    stack = None
    home = None
    details = None
    nav_stack = ['home']

    resolutions = [
        (1024, 576),
        (1156, 648),
        (1280, 760),
    ]

    def __init__(self, app):
        Gtk.Window.__init__(self, application=app)
        self.pick_resolution()
        self.build_headerbar()

        # Get main layout sorted
        self.layout = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.add(self.layout)

        self.build_search_bar()
        self.get_style_context().add_class("solus-sc")

        self.context = ScContext()

        # TODO: Fix this for updates-view handling
        self.build_content()
        self.show_all()

        # Everything setup? Let's start loading plugins
        self.context.begin_load()

    def build_content(self):
        # Main UI wrap
        scroll = Gtk.ScrolledWindow(None, None)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(
            Gtk.StackTransitionType.CROSSFADE)

        scroll.add(self.stack)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.layout.pack_start(scroll, True, True, 0)

        # Build home view now
        self.home = ScHomeView(self.context)
        self.home.connect('item-selected', self.item_selected)
        self.stack.add_named(self.home, 'home')

        # Build Details view
        self.details = ScDetailsView(self.context)
        self.stack.add_named(self.details, 'details')

    def pick_resolution(self):
        """ Attempt to pick a good 16:9 resolution for the screen """
        scr = self.get_screen()
        w = scr.get_width()
        h = scr.get_height()

        res = self.resolutions
        res.reverse()
        for res_cand in res:
            if res_cand[0] > w or res_cand[1] > h:
                continue
            print(res_cand)
            self.set_size_request(res_cand[0], res_cand[1])
            return
        self.set_size_request(800, 600)

    def build_headerbar(self):
        """ Build main nav + search """
        self.hbar = Gtk.HeaderBar()
        self.hbar.set_show_close_button(True)
        self.set_titlebar(self.hbar)
        self.set_title("Software Center")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name("system-software-install")

        # Navigation control..
        self.back_button = Gtk.Button.new_from_icon_name(
            "go-previous-symbolic",
            Gtk.IconSize.SMALL_TOOLBAR)
        self.back_button.set_can_focus(False)
        self.back_button.connect('clicked', self.on_back_clicked)
        self.hbar.pack_start(self.back_button)
        self.back_button.set_sensitive(False)

        self.search_button = Gtk.ToggleButton()
        img = Gtk.Image.new_from_icon_name(
            "edit-find-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        self.search_button.add(img)
        self.search_button.set_can_focus(False)
        st = self.search_button.get_style_context()
        st.add_class("image-button")
        self.hbar.pack_end(self.search_button)

    def handle_key_event(self, w, e=None, d=None):
        """ Proxy window navigation events to the searchbar """
        return self.search_bar.handle_event(e)

    def build_search_bar(self):
        """ Build the actual search entry, hook it up """
        # Whack in a search box
        self.search_revealer = Gtk.Revealer.new()
        self.layout.pack_start(self.search_revealer, False, False, 0)
        self.search_bar = Gtk.SearchBar.new()
        self.search_revealer.add(self.search_bar)
        self.search_entry = Gtk.SearchEntry.new()
        self.search_entry.set_size_request(400, -1)

        search_layout = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.search_bar.add(search_layout)
        search_layout.pack_start(self.search_entry, True, True, 0)
        self.search_bar.connect_entry(self.search_entry)
        self.search_revealer.set_reveal_child(True)
        self.search_entry.set_hexpand(True)
        self.search_bar.set_show_close_button(True)
        self.connect('key-press-event', self.handle_key_event)

        self.search_button.bind_property('active', self.search_bar,
                                         'search-mode-enabled',
                                         GObject.BindingFlags.BIDIRECTIONAL)

    def item_selected(self, source, item):
        """ Handle UI selection of an individual item """
        print("Item selected: {}".format(item.get_id()))
        self.details.set_item(item)
        self.push_nav("details")

    def on_back_clicked(self, btn, udata=None):
        """ User clicked the back button """
        self.nav_stack.pop()
        if len(self.nav_stack) < 2:
            self.back_button.set_sensitive(False)
        self.stack.set_visible_child_name(self.nav_stack[-1])
        self.stack.get_visible_child().grab_focus()

    def push_nav(self, page_name):
        self.nav_stack.append(page_name)
        self.back_button.set_sensitive(True)
        self.stack.set_visible_child_name(page_name)
        self.stack.get_visible_child().grab_focus()
