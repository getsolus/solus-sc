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
from gi.repository import Gio
from gi.repository import AppStreamGlib as As


class DetailsView(Gtk.VBox):
    """ Show all the details of a given package to the user as well
        as supplying them with manipulation functions, i.e. for removal, etc
    """

    # The appsystem allows us to perform queries in icons and such
    appsystem = None

    # The main header icon, hopefully from appstream
    image_icon = None

    # Display name of the package, not necessarily the .eopkg name
    label_name = None

    # The currently selected package for rendering
    package = None

    # Description for this package. Currently stripped of markup..
    label_description = None

    # Developers
    label_developers = None

    # Installed size/download size
    label_size = None

    # Version string
    label_version = None

    install_button = None
    remove_button = None
    website_button = None
    donate_button = None
    bug_button = None

    # Allow switching between our various views
    view_stack = None
    view_switcher = None

    changelog_list = None

    # Place to stick license links
    license_box = None

    # Main screenshot view
    image_widget = None

    # A box of thumbnails for selecting the main image
    box_thumbnails = None
    screen_map = None

    # Urls..
    url_website = None
    url_bug = None
    url_donate = None
    is_install_page = False
    basket = None

    fetcher = None

    def on_donate(self, btn, udata=None):
        """ Launch the donation site """
        try:
            Gtk.show_uri(None, self.url_donate, 0)
        except:
            pass

    def on_website(self, btn, udata=None):
        """ Launch the main website """
        try:
            Gtk.show_uri(None, self.url_website, 0)
        except:
            pass

    def on_bug(self, btn, udata=None):
        """ Launch the bug website """
        try:
            Gtk.show_uri(None, self.url_bug, 0)
        except:
            pass

    def on_install(self, btn, udata=None):
        """ Install a package """
        self.worker.install_package(self.package)

    def on_remove(self, btn, udata=None):
        """ Install a package """
        self.worker.remove_package(self.package)

    def __init__(self, appsystem, plugins, worker):
        Gtk.VBox.__init__(self)
        self.appsystem = appsystem
        self.plugins = plugins
        self.worker = worker

        header = Gtk.HBox(0)
        header.set_margin_top(12)
        header.set_margin_start(12)
        header.set_margin_end(12)
        header.set_margin_bottom(6)
        self.pack_start(header, False, False, 0)

        # Set up the icon
        self.image_icon = Gtk.Image.new()
        # Some padding between us and the display label..
        self.image_icon.set_margin_end(12)
        header.pack_start(self.image_icon, False, False, 0)

        # Set up the display label
        self.label_name = Gtk.Label("")
        self.label_name.set_max_width_chars(60)
        self.label_name.set_line_wrap(True)
        self.label_name.set_property("xalign", 0.0)
        header.pack_start(self.label_name, False, False, 0)
        self.label_name.set_halign(Gtk.Align.START)
        self.label_name.set_valign(Gtk.Align.START)
        self.label_name.set_margin_top(6)

        # Set up the action line
        action_line = Gtk.HBox(0)
        action_line.set_valign(Gtk.Align.CENTER)
        action_line.set_halign(Gtk.Align.END)
        header.pack_end(action_line, False, False, 0)

        # Project support links
        # Bugs
        self.bug_button = self.create_image_button(
            _("Report issues"), "help-faq-symbolic")
        self.bug_button.set_no_show_all(True)
        self.bug_button.hide()
        self.bug_button.connect("clicked", self.on_bug)
        action_line.pack_start(self.bug_button, False, False, 0)

        # Visit the website of the package
        self.website_button = self.create_image_button(
            _("Visit Website"), "web-browser-symbolic")
        self.website_button.set_no_show_all(True)
        self.website_button.hide()
        self.website_button.connect("clicked", self.on_website)
        action_line.pack_start(self.website_button, False, False, 0)

        # Main action buttons
        self.install_button = Gtk.Button(_("Install"))
        self.install_button.set_valign(Gtk.Align.CENTER)
        self.install_button.connect("clicked", self.on_install)
        self.install_button.set_can_focus(False)
        self.install_button.set_margin_start(4)
        self.install_button.get_style_context().add_class("suggested-action")
        action_line.pack_end(self.install_button, False, False, 0)
        self.install_button.set_no_show_all(True)

        # Remove button
        self.remove_button = Gtk.Button(_("Remove"))
        self.remove_button.set_valign(Gtk.Align.CENTER)
        self.remove_button.connect("clicked", self.on_remove)
        self.remove_button.set_can_focus(False)
        self.remove_button.set_margin_start(4)
        self.remove_button.get_style_context().add_class("destructive-action")
        action_line.pack_end(self.remove_button, False, False, 0)
        self.remove_button.set_no_show_all(True)

        box_body = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box_body.set_margin_start(12)
        box_body.set_margin_end(24)
        box_body.set_margin_bottom(24)
        self.scroll = Gtk.ScrolledWindow(None, None)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.add(box_body)
        self.pack_start(self.scroll, True, True, 0)

        # View switcher provides inline switcher
        self.view_switcher = Gtk.StackSwitcher()

        self.view_switcher.set_halign(Gtk.Align.CENTER)
        self.view_switcher.get_style_context().add_class("flat")
        self.view_switcher.set_can_focus(False)
        self.view_switcher.set_margin_bottom(12)

        # Apply visual quirk for adapta
        sep_valign = Gtk.Align.CENTER
        gtk_theme = self.get_settings().get_property("gtk-theme-name").lower()
        if gtk_theme.startswith("adapta"):
            sep_valign = Gtk.Align.END

        box_lines = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box_body.pack_start(box_lines, False, False, 0)
        sep1 = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        sep2 = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        sep1.set_valign(sep_valign)
        sep2.set_valign(sep_valign)
        box_lines.set_margin_start(8)
        box_lines.set_margin_end(8)
        sep1.set_margin_bottom(12)
        sep2.set_margin_bottom(12)
        box_lines.pack_start(sep1, True, True, 0)
        box_lines.pack_start(self.view_switcher, False, False, 0)
        box_lines.pack_start(sep2, True, True, 0)

        # View stack will contain our various pages
        self.view_stack = Gtk.Stack()
        box_body.pack_start(self.view_stack, True, True, 0)
        self.view_switcher.set_stack(self.view_stack)
        self.view_stack.set_homogeneous(False)
        t = Gtk.StackTransitionType.SLIDE_LEFT_RIGHT
        self.view_stack.set_transition_type(t)
        self.view_stack.set_interpolate_size(True)

        # Create pages
        self.setup_details_view()

    def create_image_button(self, label, icon):
        """ Helpful utility to create an image button """
        button = Gtk.Button.new_from_icon_name(icon, Gtk.IconSize.BUTTON)
        sc = button.get_style_context()
        sc.add_class("image-button")
        sc.add_class("circular")
        button.set_tooltip_text(label)

        button.show_all()
        button.set_hexpand(False)
        button.set_halign(Gtk.Align.CENTER)
        button.set_valign(Gtk.Align.CENTER)
        button.set_margin_start(4)
        button.set_margin_end(4)
        button.set_can_focus(False)

        return button

    def setup_details_view(self):
        self.scroll_wrap = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.view_stack.add_titled(self.scroll_wrap, "details", _("Details"))

        details_wrap = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.scroll_wrap.pack_start(details_wrap, True, True, 0)

        # Need the description down a bit and a fair bit padded
        self.label_description = Gtk.Label("")
        self.label_description.set_halign(Gtk.Align.START)
        self.label_description.set_valign(Gtk.Align.START)
        self.label_description.set_margin_top(20)
        # Deprecated but still needs using with linewrap
        self.label_description.set_property("xalign", 0.0)
        self.label_description.set_margin_start(8)
        self.label_description.set_max_width_chars(180)
        self.label_description.set_line_wrap(True)
        self.label_description.set_selectable(True)
        self.label_description.set_can_focus(False)
        details_wrap.pack_start(self.label_description, True, True, 0)

        # Begin the tail grid
        self.tail_grid = Gtk.Grid()
        self.tail_grid.set_margin_top(20)
        self.tail_grid.set_margin_start(20)
        self.tail_grid.set_row_spacing(8)
        self.tail_grid.set_column_spacing(8)
        details_wrap.pack_end(self.tail_grid, False, False, 0)

        grid_row = 0
        col_label = 0
        col_value = 1

        lab_dev = Gtk.Label(_("Developers"))
        lab_dev.set_halign(Gtk.Align.START)
        lab_dev.get_style_context().add_class("dim-label")
        self.tail_grid.attach(lab_dev, col_label, grid_row, 1, 1)

        self.label_developers_assoc = lab_dev
        self.label_developers_assoc.set_no_show_all(True)

        self.label_developers = Gtk.Label("")
        self.label_developers.set_no_show_all(True)
        self.label_developers.set_halign(Gtk.Align.START)
        self.tail_grid.attach(self.label_developers, col_value, grid_row, 1, 1)

        grid_row += 1

        lab_vers = Gtk.Label(_("Version"))
        lab_vers.set_halign(Gtk.Align.START)
        lab_vers.get_style_context().add_class("dim-label")
        self.tail_grid.attach(lab_vers, col_label, grid_row, 1, 1)

        self.label_version = Gtk.Label("")
        self.label_version.set_halign(Gtk.Align.START)
        self.tail_grid.attach(self.label_version, col_value, grid_row, 1, 1)

        grid_row += 1

        # Donation button launches website to donate to authors
        self.donate_button = Gtk.Button(_("Donate"))
        self.donate_button.connect("clicked", self.on_donate)
        self.donate_button.set_no_show_all(True)
        self.tail_grid.attach(self.donate_button, col_label, grid_row, 2, 1)

    def update_from_package(self, package):
        """ Update our view based on a given package """

        id = package.get_id()
        name = self.render_marked(self.appsystem.get_name(id, package.get_title()))
        comment = self.render_marked(self.appsystem.get_summary(id, package.get_summary()))
        description = self.appsystem.get_description(id, package.get_description())
        self.package = package

        version = package.get_version()
        self.label_version.set_markup(version)
        # Update display now.
        title_format = "<span size='x-large'><b>{}</b></span>\n{}"
        self.label_name.set_markup(title_format.format(name,
                                                       comment))
        # Sort out a nice icon
        pbuf = self.appsystem.get_pixbuf(id)
        if pbuf:
            # Handle icon theme names
            if isinstance(pbuf, Gio.ThemedIcon):
                self.image_icon.set_from_gicon(pbuf, Gtk.IconSize.DIALOG)
                self.image_icon.set_pixel_size(64)
            else:
                # Handle local files
                self.image_icon.set_from_pixbuf(pbuf)
        else:
            icon = "package-x-generic"
            self.image_icon.set_from_icon_name(icon, Gtk.IconSize.DIALOG)
            self.image_icon.set_pixel_size(64)

        # Update the description
        self.label_description.set_label(self.render_plain(description))

        dev = self.appsystem.get_developers(id)
        if not dev:
            self.label_developers.hide()
            self.label_developers_assoc.hide()
        else:
            self.label_developers.set_text(dev)
            self.label_developers.show()
            self.label_developers_assoc.show()

        # Take the appropriate action ..
        if self.is_install_page:
            self.remove_button.hide()
            self.install_button.show()
        else:
            sensitive = True
            self.install_button.hide()
            self.remove_button.show()
            if not sensitive:
                self.remove_button.set_tooltip_text(
                    _("Cannot remove core system software"))
            else:
                self.remove_button.set_tooltip_text(None)
            self.remove_button.set_sensitive(sensitive)

        # Update the homepage button
        url = self.appsystem.get_website(id, None)
        if url:
            self.url_website = url
            self.website_button.show()
        else:
            self.website_button.hide()

        donate = self.appsystem.get_donation_site(id)
        if donate:
            self.url_donate = donate
            self.donate_button.show()
        else:
            self.donate_button.hide()

        bug = self.appsystem.get_bug_site(id)
        if donate:
            self.url_bug = bug
            self.bug_button.show()
        else:
            self.bug_button.hide()

        # Switch to details view now in case they were on changelog
        self.view_stack.set_visible_child_name("details")

    def render_plain(self, input_string):
        """ Render a plain version of the description, no markdown """
        plain = As.markup_convert_simple(input_string)
        plain = plain.replace("&quot;", "\"").replace("&apos;", "'")
        return plain

    def render_marked(self, input_string):
        return self.render_plain(input_string).replace("&", "&amp;")

