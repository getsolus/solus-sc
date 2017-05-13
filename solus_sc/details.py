#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import AppStreamGlib as As
from .imagewidget import ScImageWidget
from .util import sc_format_size_local


class PackageDetailsView(Gtk.VBox):
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

    # Installed size/download size
    label_size = None

    # Package license(s)
    label_license = None

    install_button = None
    remove_button = None
    website_button = None
    donate_button = None

    # Allow switching between our various views
    view_stack = None
    view_switcher = None

    # Main screenshot view
    image_widget = None

    # Urls..
    url_website = None
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

    def on_install(self, btn, udata=None):
        """ Install a package """
        self.basket.install_package(self.package)
        self.basket.apply_operations()

    def on_remove(self, btn, udata=None):
        """ Install a package """
        self.basket.remove_package(self.package)
        self.basket.apply_operations()

    def on_basket_changed(self, basket, udata=None):
        """ Update view based on the currently selected package """
        sensitive = not self.basket.is_busy()

        self.install_button.set_sensitive(sensitive)
        self.remove_button.set_sensitive(sensitive)

        if self.basket.is_busy():
            return
        if not self.package:
            return

        if self.is_install_page:
            # Find out if this thing was actually installed ..
            if self.basket.installdb.has_package(self.package.name):
                pkg = self.basket.installdb.get_package(self.package.name)
                self.is_install_page = False
                self.update_from_package(pkg)
        else:
            # We're a remove package, see if we removed our thing
            if not self.basket.installdb.has_package(self.package.name):
                # Offer installing
                if not self.basket.packagedb.has_package(self.package.name):
                    print("Unknown local package .... ")
                    return
                pkg = self.basket.packagedb.get_package(self.package.name)
                self.is_install_page = True
                self.update_from_package(pkg)

    def on_media_fetched(self, fetcher, uri, filename, pixbuf):
        """ Some media that we asked for has been loaded """
        # Check if its our main preview
        if uri == self.image_widget.uri:
            self.image_widget.show_image(uri, pixbuf)
            self.image_widget.set_size_request(-1, -1)
            self.image_widget.queue_resize()
        pixbuf = None

    def on_fetch_failed(self, fetcher, uri, err):
        """ We failed to fetch *something* """
        self.image_widget.show_failed(uri, err)
        self.image_widget.set_size_request(-1, -1)
        self.image_widget.queue_resize()

    def __init__(self, appsystem, basket):
        Gtk.VBox.__init__(self)
        self.appsystem = appsystem
        self.basket = basket
        self.basket.connect("basket-changed", self.on_basket_changed)

        # Bind a weak reference for later usage
        self.fetcher = appsystem.fetcher
        self.fetcher.connect('media-fetched', self.on_media_fetched)
        self.fetcher.connect('fetch-failed', self.on_fetch_failed)

        header = Gtk.HBox(0)
        header.set_border_width(24)
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
        self.install_button = Gtk.Button(_("Install"))
        self.install_button.connect("clicked", self.on_install)
        self.install_button.set_can_focus(False)
        self.install_button.get_style_context().add_class("suggested-action")
        action_line.pack_end(self.install_button, False, False, 0)
        self.install_button.set_no_show_all(True)

        # Remove button
        self.remove_button = Gtk.Button(_("Remove"))
        self.remove_button.connect("clicked", self.on_remove)
        self.remove_button.set_can_focus(False)
        self.remove_button.get_style_context().add_class("destructive-action")
        action_line.pack_end(self.remove_button, False, False, 0)
        self.remove_button.set_no_show_all(True)

        box_body = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box_body.set_margin_start(24)
        box_body.set_margin_end(24)
        box_body.set_margin_bottom(24)
        self.scroll = Gtk.ScrolledWindow(None, None)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.add(box_body)
        self.pack_start(self.scroll, True, True, 0)

        # Now set up the screenshot section
        self.image_widget = ScImageWidget()
        self.image_widget.set_margin_bottom(30)
        box_body.pack_start(self.image_widget, False, False, 0)

        # View switcher provides inline switcher
        self.view_switcher = Gtk.StackSwitcher()
        self.view_switcher.get_style_context().add_class("flat")
        self.view_switcher.set_can_focus(False)
        box_body.pack_start(self.view_switcher, False, False, 0)

        # View stack will contain our various pages
        self.view_stack = Gtk.Stack()
        box_body.pack_start(self.view_stack, True, True, 0)
        self.view_switcher.set_stack(self.view_stack)
        self.view_switcher.set_halign(Gtk.Align.START)

        # Create pages
        self.setup_details_view()
        self.setup_changelog_view()

    def setup_details_view(self):
        self.scroll_wrap = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.view_stack.add_titled(self.scroll_wrap, "details", _("Details"))

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
        self.scroll_wrap.pack_start(self.label_description, True, True, 0)

        # Begin the tail grid
        self.tail_grid = Gtk.Grid()
        self.tail_grid.set_margin_top(20)
        self.tail_grid.set_margin_start(20)
        self.tail_grid.set_row_spacing(8)
        self.tail_grid.set_column_spacing(8)
        self.scroll_wrap.pack_end(self.tail_grid, False, False, 0)

        grid_row = 0
        col_label = 0
        col_value = 1

        # Size of the package when installed locally
        self.label_installed = Gtk.Label(_("Installed size"))
        self.label_installed.set_halign(Gtk.Align.END)
        self.label_installed.get_style_context().add_class("dim-label")
        self.tail_grid.attach(self.label_installed, col_label, grid_row, 1, 1)

        self.label_size = Gtk.Label("")
        self.label_size.set_halign(Gtk.Align.START)
        self.tail_grid.attach(self.label_size, col_value, grid_row, 1, 1)

        grid_row += 1

        # License field
        label_license_field = Gtk.Label(_("License"))
        label_license_field.set_halign(Gtk.Align.END)
        label_license_field.get_style_context().add_class("dim-label")
        self.tail_grid.attach(label_license_field, col_label, grid_row, 1, 1)

        self.label_license = Gtk.Label("")
        self.label_license.set_halign(Gtk.Align.START)
        self.tail_grid.attach(self.label_license, col_value, grid_row, 1, 1)

        grid_row += 1

        # TODO: Make this stuff way less ugly.
        # Visit the website of the package
        self.website_button = Gtk.Button(_("Website"))
        self.website_button.set_no_show_all(True)
        self.website_button.connect("clicked", self.on_website)
        self.tail_grid.attach(self.website_button, col_label, grid_row, 2, 1)

        grid_row += 1

        # Donation button launches website to donate to authors
        self.donate_button = Gtk.Button(_("Donate"))
        self.donate_button.connect("clicked", self.on_donate)
        self.donate_button.set_no_show_all(True)
        self.tail_grid.attach(self.donate_button, col_label, grid_row, 2, 1)

    def setup_changelog_view(self):
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.view_stack.add_titled(box, "changelog", _("Changelog"))

    def update_from_package(self, package):
        """ Update our view based on a given package """

        name = self.appsystem.get_name(package)
        comment = self.appsystem.get_summary(package)
        description = self.appsystem.get_description(package)
        self.package = package
        self.setup_screenshots(package)

        version = "{}-{}".format(str(package.version), str(package.release))
        # Update display now.
        title_format = "<span size='x-large'><b>{}</b> - {}</span>\n{}"
        self.label_name.set_markup(title_format.format(name,
                                                       version,
                                                       comment))
        licenses = u" | ".join([str(x) for x in package.license])
        self.label_license.set_text(licenses)

        # Sort out a nice icon
        pbuf = self.appsystem.get_pixbuf(package)
        if pbuf:
            # Handle icon theme names
            if isinstance(pbuf, Gio.ThemedIcon):
                self.image_icon.set_from_gicon(pbuf, Gtk.IconSize.DIALOG)
                self.image_icon.set_pixel_size(64)
            else:
                # Handle local files
                self.image_icon.set_from_pixbuf(pbuf)
        else:
            icon = self.appsystem.get_icon(package)
            self.image_icon.set_from_icon_name(icon, Gtk.IconSize.DIALOG)
            self.image_icon.set_pixel_size(64)

        # Update the description
        self.label_description.set_label(self.render_plain(description))

        # Take the appropriate action ..
        if self.is_install_page:
            self.remove_button.hide()
            self.install_button.show()
        else:
            sensitive = package.partOf != "system.base"
            self.install_button.hide()
            self.remove_button.show()
            if not sensitive:
                self.remove_button.set_tooltip_text(
                    _("Cannot remove core system software"))
            else:
                self.remove_button.set_tooltip_text(None)
            self.remove_button.set_sensitive(sensitive)

        # Update the homepage button
        url = self.appsystem.get_website(package)
        if url:
            self.url_website = url
            self.website_button.show()
        else:
            self.website_button.hide()

        donate = self.appsystem.get_donation_site(package)
        if donate:
            self.url_donate = donate
            self.donate_button.show()
        else:
            self.donate_button.hide()

        size = sc_format_size_local(package.installedSize)
        self.label_size.set_markup(size)

    def render_plain(self, input_string):
        """ Render a plain version of the description, no markdown """
        plain = As.markup_convert_simple(input_string)
        plain = plain.replace("&quot;", "\"").replace("&apos;", "'")
        return plain

    def setup_screenshots(self, package):
        screens = self.appsystem.get_screenshots(package)
        if not screens:
            self.image_widget.show_not_found()
            self.image_widget.set_size_request(-1, -1)
            self.image_widget.queue_resize()
            return
        # Update the UI immediately to show we're going to load
        self.image_widget.show_loading()
        default = None
        for scr in screens:
            if scr.default:
                default = scr
        if not default:
            default = screens[0]
        self.image_widget.uri = default.main_uri
        # Always "fetch", fetcher knows if it exists or not.
        self.fetcher.fetch_media(default.main_uri)
