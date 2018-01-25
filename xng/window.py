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

from gi.repository import Gtk, GObject, GLib
from .context import ScContext
from .home import ScHomeView
from .details import ScDetailsView


class ScUpdatesButton(Gtk.Button):
    """ ScUpdatesButton is a simple button wrapper to allow hiding the
        updates text until such point as the button is needed fully

        When updates are available, the button style class is updated
        and we expand the text out to the left of the button, to
        provide a visual cue to the user that there has been an internal
        state change.
    """

    revealer = None
    label = None
    img = None

    def __init__(self):
        Gtk.Button.__init__(self)

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.add(box)

        # Image is anchored on the left
        self.img = Gtk.Image.new_from_icon_name(
            "software-update-available-symbolic",
            Gtk.IconSize.SMALL_TOOLBAR)
        box.pack_start(self.img, True, True, 0)

        # Revealer will slide the label out
        self.revealer = Gtk.Revealer()
        self.label = Gtk.Label.new("Updates available")
        self.label.get_style_context().add_class("small-title")
        self.revealer.add(self.label)
        self.revealer.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_LEFT)
        self.revealer.set_reveal_child(False)
        box.pack_start(self.revealer, False, False, 0)

    def set_updates_available(self, available):
        """ Alter our state to indicate update availability """
        stclass = "suggested-action"
        if available:
            self.get_style_context().add_class(stclass)
            self.label.set_margin_start(6)
        else:
            self.label.set_margin_start(0)
            self.get_style_context().remove_class(stclass)

        self.revealer.set_reveal_child(available)

        # Just helps with idle loops
        return False


class ScMainWindow(Gtk.ApplicationWindow):

    # Headerbar
    hbar = None
    search_button = None
    back_button = None
    home_button = None
    updates_button = None

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

        self.set_current_page("home")

        # Everything setup? Let's start loading plugins
        self.context.begin_load()

        GLib.timeout_add(
            3000, lambda: self.updates_button.set_updates_available(True))

    def build_content(self):
        # Main UI wrap
        scroll = Gtk.ScrolledWindow(None, None)

        self.stack = Gtk.Stack()
        self.stack.set_homogeneous(False)
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

        # Go home, instead of requiring a tabbed view
        self.home_button = Gtk.Button.new_from_icon_name(
            "go-home-symbolic",
            Gtk.IconSize.SMALL_TOOLBAR)
        self.home_button.set_can_focus(False)
        self.home_button.connect('clicked', self.on_home_clicked)
        self.hbar.pack_start(self.home_button)
        self.home_button.set_sensitive(False)

        self.search_button = Gtk.ToggleButton()
        img = Gtk.Image.new_from_icon_name(
            "edit-find-symbolic", Gtk.IconSize.SMALL_TOOLBAR)
        self.search_button.add(img)
        self.search_button.set_can_focus(False)
        st = self.search_button.get_style_context()
        st.add_class("image-button")
        self.hbar.pack_end(self.search_button)

        # Update button position won't affect search button placement
        self.updates_button = ScUpdatesButton()
        self.hbar.pack_end(self.updates_button)

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
        self.set_current_page(self.nav_stack[-1])

    def on_home_clicked(self, btn, udata=None):
        """ Clicked home, reset nav stack, set page to home """
        self.nav_stack = ["home"]
        self.back_button.set_sensitive(False)
        self.set_current_page("home")

    def push_nav(self, page_name):
        """ Push a new page in the nav stack """
        self.nav_stack.append(page_name)
        self.back_button.set_sensitive(True)
        self.set_current_page(page_name)

    def set_current_page(self, name):
        """ Handle changing the current page """
        self.stack.set_visible_child_name(name)
        self.stack.get_visible_child().grab_focus()
        self.hbar.set_subtitle(self.stack.get_visible_child().get_page_name())
        self.home_button.set_sensitive(name != "home")
