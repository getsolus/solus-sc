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

from gi.repository import Gtk, GObject, GLib, Gdk
from .context import ScContext
from .home import ScHomeView
from .categories import ScCategoriesView
from .details import ScDetailsView
from .featured import ScFeaturedEmbed
from .loadpage import ScLoadingPage
from .updates import ScUpdatesView
from .search import ScSearchView
from .plugins.base import SearchRequest
from .drawer import ScDrawerPlane


class ScUpdatesButton(Gtk.Button):
    """ Simple button that restyles itself when updates are available
    """

    img = None

    def __init__(self):
        Gtk.Button.__init__(self)

        self.img = Gtk.Image.new_from_icon_name(
            "software-update-available-symbolic",
            Gtk.IconSize.SMALL_TOOLBAR)
        self.add(self.img)

    def set_updates_available(self, available):
        """ Alter our state to indicate update availability """
        stclass = "suggested-action"
        if available:
            self.set_tooltip_text(_("Updates available"))
            self.get_style_context().add_class(stclass)
        else:
            self.set_tooltip_text(_("Check for updates"))
            self.get_style_context().remove_class(stclass)

        # Just helps with idle loops
        return False


class ScDrawerButton(Gtk.ToggleButton):
    """ Simple button to control the draw visibility, and also sliding
        a spinner into view when jobs are currently running
    """

    revealer = None
    spinner = None
    context = None

    def __init__(self, context):
        Gtk.ToggleButton.__init__(self)
        self.context = context

        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.add(box)

        # Image is anchored on the left
        self.img = Gtk.Image.new_from_icon_name(
            "open-menu-symbolic",
            Gtk.IconSize.SMALL_TOOLBAR)
        box.pack_start(self.img, True, True, 0)
        self.img.set_halign(Gtk.Align.CENTER)

        self.set_can_focus(False)
        self.get_style_context().add_class("image-button")

        # Allow sliding the spinner into view
        self.revealer = Gtk.Revealer.new()
        self.revealer.set_reveal_child(False)
        self.revealer.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_RIGHT)
        self.spinner = Gtk.Spinner.new()
        self.spinner.stop()
        self.revealer.add(self.spinner)
        box.pack_start(self.revealer, False, False, 0)
        self.revealer.set_property("margin", 0)
        self.revealer.set_border_width(0)

        self.spinner.set_margin_start(3)
        self.spinner.set_margin_end(3)

        # Allow knowing job states
        self.context.executor.connect('execution-started', self.start_exec)
        self.context.executor.connect('execution-ended', self.end_exec)

    def start_exec(self, executor):
        """ Execution started, show the busy spinner """
        self.spinner.start()
        self.revealer.set_reveal_child(True)

    def end_exec(self, executor):
        """ Execution stopped, hide the busy spinner """
        self.spinner.stop()
        self.revealer.set_reveal_child(False)


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
    search_installed_only = None
    request = None

    mode_open = None

    featured = None

    # Tracking
    context = None
    scroll = None
    stack = None
    home = None
    details = None
    updates = None
    search = None
    categories = None
    nav_stack = ['home']
    busy = False

    overlay = None
    drawer = None

    resolutions = [
        (1024, 576),
        (1156, 648),
        (1280, 760),
    ]

    # Allow tracking all pages.
    pages = None

    def __init__(self, app):
        Gtk.Window.__init__(self, application=app)
        self.pick_resolution()

        # Get main layout sorted
        self.layout = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.overlay = Gtk.Overlay.new()
        self.add(self.overlay)
        self.overlay.add(self.layout)

        self.get_style_context().add_class("solus-sc")

        self.context = ScContext(self)
        self.context.connect('loaded', self.on_context_loaded)

        self.drawer = ScDrawerPlane(self.context)
        self.overlay.add_overlay(self.drawer)

        self.build_headerbar()
        self.build_search_bar()

        # TODO: Fix this for updates-view handling
        self.build_featured()
        self.build_content()
        self.show_all()

        # Keep this tracked.
        self.pages = [
            self.home,
            self.details,
            self.categories,
            self.loading,
            self.updates,
            self.search,
        ]

        self.loading.start()
        self.set_current_page("loading")
        self.set_busy(True)

        # Everything setup? Let's start loading plugins
        self.context.begin_load()

        # Handle events
        self.connect("button-release-event", self.on_button_release_event)

        # Stupid hack
        GLib.timeout_add(
            3000, lambda: self.updates_button.set_updates_available(True))

    def set_busy(self, busy):
        """ Mark the window as busy and prevent further navigation """
        self.busy = busy
        self.back_button.set_sensitive(not busy)
        self.home_button.set_sensitive(not busy)
        self.search_button.set_sensitive(not busy)
        self.updates_button.set_sensitive(not busy)
        self.search_entry.set_sensitive(not busy)
        self.search_installed_only.set_sensitive(not busy)

    def on_context_loaded(self, context):
        """ We now have featured, so we're half way through initial loading """
        self.loading.set_message()

    def done(self):
        """ All loading completed """
        self.set_current_page("home")
        self.loading.stop()
        self.set_busy(False)
        GLib.idle_add(self.begin_refresh)
        return False

    def begin_refresh(self):
        self.context.refresh_sources()
        return False

    def build_featured(self):
        """ Build the featured-items header """
        self.featured = ScFeaturedEmbed(self.context)
        self.featured.widget.connect('item-selected', self.item_selected)
        self.layout.pack_start(self.featured, False, False, 0)

    def build_content(self):
        # Main UI wrap
        self.scroll = Gtk.ScrolledWindow(None, None)

        self.stack = Gtk.Stack()
        self.stack.set_homogeneous(False)
        self.stack.set_transition_type(
            Gtk.StackTransitionType.CROSSFADE)

        self.scroll.add(self.stack)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.layout.pack_start(self.scroll, True, True, 0)

        # We need loading view first.
        self.loading = ScLoadingPage()
        self.loading.set_message(_("Waking up with a smile"))
        self.stack.add_named(self.loading, 'loading')

        # Build home view now
        self.home = ScHomeView(self.context)
        self.home.connect('item-selected', self.item_selected)
        self.home.connect('category-selected', self.category_selected)
        self.stack.add_named(self.home, 'home')

        # Categories view
        self.categories = ScCategoriesView(self.context)
        self.categories.connect('item-selected', self.item_selected)
        self.stack.add_named(self.categories, 'categories')

        # Build Details view
        self.details = ScDetailsView(self.context)
        self.stack.add_named(self.details, 'details')

        # Build updates view
        self.updates = ScUpdatesView(self.context)
        self.stack.add_named(self.updates, 'updates')

        # Build search view
        self.search = ScSearchView(self.context)
        self.stack.add_named(self.search, 'search')
        self.search.connect('item-selected', self.item_selected)

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

        # Toggle for sidebar drawer
        self.sidebar_button = ScDrawerButton(self.context)
        self.sidebar_button.connect('toggled', self.on_sidebar_toggled)
        self.hbar.pack_end(self.sidebar_button)

        self.sidebar_button.bind_property('active',
                                          self.drawer,
                                          'drawer-visible',
                                          GObject.BindingFlags.BIDIRECTIONAL)

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
        self.updates_button.connect("clicked", self.on_updates_clicked)
        self.hbar.pack_end(self.updates_button)

    def on_sidebar_toggled(self, widget, udata=None):
        if widget.get_active():
            self.drawer.slide_in()
        else:
            self.drawer.slide_out()

    def on_updates_clicked(self, widget, udata=None):
        self.push_nav("updates")

    def handle_key_event(self, w, e=None, d=None):
        """ Proxy window navigation events to the searchbar """
        if self.busy or self.drawer.drawer_visible:
            return self.drawer.handle_key_event(e)
        return self.search_bar.handle_event(e)

    def build_search_bar(self):
        """ Build the actual search entry, hook it up """
        # Whack in a search box
        self.search_revealer = Gtk.Revealer.new()
        self.layout.pack_start(self.search_revealer, False, False, 0)
        self.search_bar = Gtk.SearchBar.new()
        self.search_revealer.add(self.search_bar)
        self.search_entry = Gtk.SearchEntry.new()
        self.search_entry.set_hexpand(True)
        self.search_entry.set_size_request(400, -1)

        search_options = Gtk.Grid.new()
        search_options.set_row_spacing(6)
        search_options.attach(self.search_entry, 0, 0, 1, 1)
        self.search_installed_only = Gtk.CheckButton.new_with_label(
            _("Only show installed software"))
        self.search_installed_only.connect('toggled', self.on_install_change)
        search_options.attach(self.search_installed_only,
                              0, 1, 1, 1)

        self.search_bar.add(search_options)
        self.search_bar.connect_entry(self.search_entry)
        self.search_revealer.set_reveal_child(True)
        self.search_entry.set_hexpand(True)
        self.connect('key-press-event', self.handle_key_event)
        self.search_entry.connect('activate', self.on_search_activate)

        self.search_button.bind_property('active', self.search_bar,
                                         'search-mode-enabled',
                                         GObject.BindingFlags.BIDIRECTIONAL)

    def on_install_change(self, widget, udata=None):
        """ The Installed-Only filter was toggled """
        if not self.request:
            return
        self.on_search_activate(self.search_entry, None)

    def on_search_activate(self, widget, udata=None):
        """ User activated a search """
        text = self.search_entry.get_text().strip()
        if len(text) < 1:
            return

        # Set the search term so we're already in loading mode and threading
        # to the result yield.
        request = SearchRequest(text)
        request.set_installed_only(self.search_installed_only.get_active())
        self.search.set_search_request(request)
        self.request = request  # Cache for resetting the text

        # Allow moving to the search now
        self.push_nav("search")

    def item_selected(self, source, item):
        """ Handle UI selection of an individual item """
        print("Item selected: {}".format(item.get_id()))
        self.details.set_item(item)
        self.push_nav("details")

    def category_selected(self, source, category):
        """ Handle UI selection of a root-level category """
        print("Category selected: {}".format(category.get_id()))
        self.categories.set_category(category)
        self.push_nav("categories")

    def on_back_clicked(self, btn, udata=None):
        """ User clicked the back button """
        if len(self.nav_stack) < 2:
            # Already no nav..
            return
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
        if len(self.nav_stack) > 0 and self.nav_stack[-1] == page_name:
            return
        self.nav_stack.append(page_name)
        self.back_button.set_sensitive(True)
        self.set_current_page(page_name)

    def set_current_page(self, name):
        """ Handle changing the current page """
        cur = self.stack.get_visible_child_name()

        # Return child name.
        def child_nom(o):
            return o.get_parent().child_get_property(o, "name")

        # Find all children not in our current transition set
        pg = [x for x in self.pages if child_nom(x) != cur and
              child_nom(x) != name]

        # Hide all pages not part of the transition to unbugger the UI
        for page in self.pages:
            if page in pg:
                page.hide()
            else:
                page.show_all()

        self.search_button.set_active(name == 'search')
        if self.request and name == 'search':
            self.search_entry.set_text(self.request.get_term())
            self.search_entry.grab_focus()

        self.stack.set_visible_child_name(name)
        self.stack.get_visible_child().grab_focus()
        self.hbar.set_subtitle(self.stack.get_visible_child().get_page_name())
        self.home_button.set_sensitive(name != "home")

        if name == "home":
            self.featured.slide_down_show()
        else:
            self.featured.slide_up_hide()

        GObject.idle_add(self.reset_scroller)

    def reset_scroller(self):
        """ Reset scroll when tweening views """
        policy = self.scroll.get_vadjustment()
        policy.set_value(0)
        policy = self.scroll.get_hadjustment()
        policy.set_value(0)
        return False

    def on_button_release_event(self, widget, event=None):
        """ Handle "back button" on mouse """
        if event.button != 8:
            return Gdk.EVENT_PROPAGATE

        # Tell the drawer to handle it
        if self.drawer.drawer_visible:
            self.drawer.perform_back()
            return Gdk.EVENT_STOP

        # Tell us to handle it..
        if self.back_button.get_sensitive():
            self.on_back_clicked(self.back_button, event)
            return Gdk.EVENT_STOP

        return Gdk.EVENT_PROPAGATE
