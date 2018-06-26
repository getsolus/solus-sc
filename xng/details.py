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

from gi.repository import Gio, Gtk, GLib
from .screenshot_view import ScScreenshotView
from .util.markdown import SpecialMarkdownParser
from .plugins.base import ItemStatus, ItemLink
from gi.repository import AppStreamGlib as As


class ScDetailsView(Gtk.Box):
    """ Shows details for a selected ProviderItem

        The details view is effectively the pretty view with all the relevant
        package/software details, screenshots, and actions to invoke removal,
        installation, etc.
    """

    __gtype_name__ = "ScDetailsView"

    context = None
    item = None

    # Header widgets
    header_name = None
    header_image = None
    header_summary = None

    # TODO: Make less dumb
    header_action_remove = None
    header_action_install = None
    header_action_upgrade = None
    header_action_launch = None

    launch_info = None

    stack = None
    stack_switcher = None

    screenie_view = None

    # We actually put lots of labels in this guy.
    description_box = None
    parser = None

    label_version = None
    label_version_id = None
    label_website = None
    label_bugsite = None
    label_donate = None
    label_developer = None

    changelog_view = None

    def get_page_name(self):
        return self.header_name.get_text()

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.context = context
        self.parser = SpecialMarkdownParser()

        self.build_header()
        self.show_all()

    def set_item(self, item):
        """ Update our UI for the current item """
        if item == self.item:
            return

        # Only show changelog for supported items
        self.changelog_view.set_visible(
            item.has_status(ItemStatus.META_CHANGELOG))

        self.launch_info = None
        self.item = item

        # Grab the app
        apps = self.context.appsystem
        store = item.get_store()
        id = item.get_id()

        # Update main header
        self.header_name.set_markup(apps.get_name(id, item.get_name(), store))
        self.header_summary.set_markup(
            apps.get_summary(id, item.get_summary(), store))
        apps.set_image_from_item(self.header_image, item, store)
        self.header_image.set_pixel_size(64)

        if self.item.has_status(ItemStatus.INSTALLED):
            launch_id = apps.get_launchable_id(id, store)
            if launch_id is not None:
                try:
                    self.launch_info = Gio.DesktopAppInfo.new(launch_id)
                except Exception as e:
                    self.launch_info = None
                    print("Request AppStream data rebuild for: {}".format(
                        launch_id))
                    print(e)

        # Now set the screenshot ball in motion
        self.screenie_view.set_item(item)

        self.update_description()
        self.update_actions()
        self.update_details()
        self.update_links()

        # Always re-focus to details
        self.stack.set_visible_child_name("details")

    def build_header(self):
        """ Build our main header area """
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.set_margin_top(15)
        box.set_margin_left(15)
        box.set_margin_right(15)

        box_main_wrap = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box_main_wrap.pack_start(box, False, False, 0)
        ebox = Gtk.EventBox()
        ebox.add(box_main_wrap)
        ebox.get_style_context().add_class("details-header")
        self.pack_start(ebox, False, False, 0)

        self.header_name = Gtk.Label("")
        self.header_name.get_style_context().add_class("huge-label")
        self.header_image = Gtk.Image()
        self.header_image.set_pixel_size(64)
        self.header_image.set_margin_end(24)
        self.header_image.set_margin_start(12)

        box.pack_start(self.header_image, False, False, 0)

        details_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.pack_start(details_box, True, True, 0)

        # name
        self.header_name.set_halign(Gtk.Align.START)
        self.header_name.set_halign(Gtk.Align.START)
        details_box.pack_start(self.header_name, True, True, 0)

        # summary
        self.header_summary = Gtk.Label("")
        self.header_summary.set_margin_top(6)
        self.header_summary.set_margin_bottom(3)
        self.header_summary.set_halign(Gtk.Align.START)
        details_box.pack_start(self.header_summary, False, False, 0)

        # Install thing
        self.header_action_install = Gtk.Button("Install")
        self.header_action_install.connect('clicked',
                                           self.on_install_clicked)
        self.header_action_install.set_valign(Gtk.Align.CENTER)
        self.header_action_install.set_no_show_all(True)
        self.header_action_install.get_style_context().add_class(
            "suggested-action")
        self.header_action_install.set_margin_end(2)
        box.pack_end(self.header_action_install, False, False, 0)

        # Remove thing
        self.header_action_remove = Gtk.Button("Remove")
        self.header_action_remove.set_margin_end(2)
        self.header_action_remove.connect('clicked',
                                          self.on_remove_clicked)
        self.header_action_remove.set_valign(Gtk.Align.CENTER)
        self.header_action_remove.set_no_show_all(True)
        self.header_action_remove.get_style_context().add_class(
            "destructive-action")
        box.pack_end(self.header_action_remove, False, False, 0)

        # Upgrade thing
        self.header_action_upgrade = Gtk.Button("Upgrade")
        self.header_action_upgrade.set_margin_end(2)
        self.header_action_upgrade.set_valign(Gtk.Align.CENTER)
        self.header_action_upgrade.set_no_show_all(True)
        self.header_action_upgrade.get_style_context().add_class(
            "suggested-action")
        box.pack_end(self.header_action_upgrade, False, False, 0)

        self.header_action_launch = Gtk.Button.new_from_icon_name(
            "document-open-symbolic", Gtk.IconSize.BUTTON)
        self.header_action_launch.set_margin_end(4)
        self.header_action_launch.set_tooltip_text(_("Launch"))
        self.header_action_launch.connect('clicked',
                                          self.on_launch_clicked)
        self.header_action_launch.set_valign(Gtk.Align.CENTER)
        self.header_action_launch.set_no_show_all(True)
        self.header_action_launch.set_relief(Gtk.ReliefStyle.NONE)
        box.pack_end(self.header_action_launch, False, False, 0)

        self.stack = Gtk.Stack()
        self.stack.set_homogeneous(False)
        self.stack_switcher = Gtk.StackSwitcher()
        self.stack_switcher.show_all()
        self.stack_switcher.set_no_show_all(True)
        self.stack_switcher.set_halign(Gtk.Align.CENTER)
        self.stack_switcher.set_stack(self.stack)
        self.stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        box_main_wrap.pack_start(self.stack_switcher, False, False, 0)
        self.pack_start(self.stack, True, True, 0)

        # Dummy pages for now
        self.build_details()

        self.changelog_view = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.changelog_view.show_all()
        self.changelog_view.set_no_show_all(True)
        self.stack.add_titled(self.changelog_view, "changelog", "Changelog")

    def build_details(self):
        """ Build the main 'Details' view """
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.set_margin_start(40)
        box.set_margin_end(40)
        box.set_margin_bottom(40)
        self.stack.add_titled(box, "details", "Details")

        # Allocate our screenshot view area
        self.screenie_view = ScScreenshotView(self.context)
        self.screenie_view.set_halign(Gtk.Align.CENTER)
        box.pack_start(self.screenie_view, False, False, 0)

        self.build_header_section(_("Description"), box)
        # A place to have our description
        self.description_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.description_box.set_margin_end(150)
        self.description_box.set_margin_start(30)
        box.pack_start(self.description_box, False, False, 0)

        self.build_details_grid(box)

    def build_header_section(self, label, pack_target):
        """ Build a fancy header section and put it into pack_target """
        # Header for the information
        lab = Gtk.Label.new(label)
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.START)
        lab.set_margin_start(30)
        lab.set_margin_top(30)
        lab.get_style_context().add_class("dim-label")
        pack_target.pack_start(lab, False, False, 0)

        # Visually separate this information now
        sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        sep.set_margin_start(30)
        sep.set_margin_end(150)
        sep.set_margin_top(8)
        sep.set_margin_bottom(15)
        pack_target.pack_start(sep, False, False, 0)

    def build_details_grid(self, box):
        """ Build the detailed information grid for each item """
        grid = Gtk.Grid.new()
        grid.set_margin_end(150)
        grid.set_margin_start(30)
        grid.set_column_spacing(6)
        grid.set_row_spacing(12)
        grid.set_valign(Gtk.Align.START)

        self.build_header_section(_("Information"), box)

        # Attach grid to the view
        box.pack_start(grid, False, False, 0)

        self.label_version = Gtk.Label.new("")
        self.label_version.set_halign(Gtk.Align.START)
        self.label_version.show_all()
        self.label_version.set_no_show_all(True)
        desc = Gtk.Label.new(_("Version"))
        desc.set_halign(Gtk.Align.START)
        desc.set_use_markup(True)
        self.label_version_id = desc
        self.label_version_id.show_all()
        self.label_version_id.set_no_show_all(True)

        # column row
        grid.attach(desc, 0, 0, 1, 1)
        grid.attach(self.label_version, 1, 0, 1, 1)

        # create buttons for website, donations, etc
        self.label_website = Gtk.LinkButton.new(_("Visit website"))
        self.label_website.get_style_context().add_class("flat")
        self.label_bugsite = Gtk.LinkButton.new(_("Report a bug"))
        self.label_bugsite.get_style_context().add_class("flat")
        self.label_donate = Gtk.LinkButton.new(_("Make a donation"))
        self.label_donate.get_style_context().add_class("flat")

        button_box = Gtk.ButtonBox.new(Gtk.Orientation.HORIZONTAL)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_hexpand(True)
        button_box.set_layout(Gtk.ButtonBoxStyle.END)
        button_box.add(self.label_website)
        button_box.add(self.label_bugsite)
        button_box.add(self.label_donate)

        button_box.show_all()
        self.label_website.set_no_show_all(True)
        self.label_bugsite.set_no_show_all(True)
        self.label_donate.set_no_show_all(True)

        grid.attach(button_box, 2, 0, 1, 1)

        self.label_developer = Gtk.Label.new("")
        self.label_developer.set_margin_top(6)
        self.label_developer.set_margin_end(6)
        self.label_developer.set_halign(Gtk.Align.END)
        self.label_developer.set_hexpand(True)
        self.label_developer.show_all()
        self.label_developer.set_no_show_all(True)

        grid.attach(self.label_developer, 2, 1, 1, 1)

    def update_description(self):
        # I have become GTK - Destroyer Of Children
        for child in self.description_box.get_children():
            child.destroy()

        id = self.item.get_id()
        fallback = self.item.get_description()
        store = self.item.get_store()
        desc = self.context.appsystem.get_description(id, fallback, store)

        plain = As.markup_convert(desc, As.MarkupConvertFormat.MARKDOWN)
        lines = []
        try:
            self.parser.consume(plain)
            lines = self.parser.emit()
        except Exception as e:
            print("Parsing error: {}".format(e))
            plain = As.markup_convert_simple(desc)
            lines = plain.split("\n")

        for line in lines:
            lab = Gtk.Label(line)
            lab.set_use_markup(True)
            lab.set_halign(Gtk.Align.START)
            lab.set_line_wrap(True)
            lab.set_property("xalign", 0.0)
            lab.set_property("margin", 2)
            lab.set_margin_bottom(4)
            self.description_box.pack_start(lab, False, False, 0)
            lab.show_all()

    def update_actions(self):
        """ Update actions for the given item """
        # Special case for hardware, none of the buttons will do anything.
        if self.item.has_status(ItemStatus.META_VIRTUAL):
            self.header_action_install.hide()
            self.header_action_launch.hide()
            self.header_action_remove.hide()
            self.header_action_upgrade.hide()
            return

        # Normal software
        if self.item.has_status(ItemStatus.INSTALLED):
            self.header_action_remove.show()
            self.header_action_install.hide()
            if self.launch_info is not None:
                self.header_action_launch.show()
        else:
            self.header_action_remove.hide()
            self.header_action_install.show()

        # Disable remove button if dangerous!
        if self.item.has_status(ItemStatus.META_ESSENTIAL):
            self.header_action_remove.set_sensitive(False)
        else:
            self.header_action_remove.set_sensitive(True)

        if self.item.has_status(ItemStatus.UPDATE_NEEDED):
            self.header_action_upgrade.show()
        else:
            self.header_action_upgrade.hide()

        # Hide launch info once more
        if not self.launch_info:
            self.header_action_launch.hide()

    def update_details(self):
        """ Update extra detail labels from the selected package """
        version = self.item.get_version()

        # Only render version if we have one.
        if not version:
            self.label_version.hide()
            self.label_version_id.hide()
        else:
            self.label_version.show()
            self.label_version_id.show()
            self.label_version.set_markup("<b>{}</b>".format(
                self.item.get_version()))

        id = self.item.get_id()
        store = self.item.get_store()

        # Main website
        site = self.context.appsystem.get_website(id, store)
        if site:
            self.label_website.set_uri(site)
        self.label_website.set_visited(False)
        self.label_website.set_visible(site is not None)

        # Bug website
        site = self.context.appsystem.get_bug_site(id, store)
        if site:
            self.label_bugsite.set_uri(site)
        self.label_bugsite.set_visited(False)
        self.label_bugsite.set_visible(site is not None)

        # Donate website
        site = self.context.appsystem.get_donation_site(id, store)
        if site:
            self.label_donate.set_uri(site)
        self.label_donate.set_visited(False)
        self.label_donate.set_visible(site is not None)

        dev = self.context.appsystem.get_developers(id, store)
        if dev:
            developers = GLib.markup_escape_text(dev)
            self.label_developer.set_markup("Developed by <b>{}</b>".format(
                developers))
        else:
            self.label_developer.set_markup("")
        self.label_developer.set_visible(dev is not None)

    def update_links(self):
        """ Deal with ItemLink reasons """
        id = self.item.get_id()
        for reason in self.item.links:
            names = [x.get_name() for x in self.item.links[reason]]
            if reason == ItemLink.ENHANCES:
                print("{} Enhanced by: {}".format(id, names))
            else:
                print("Providers for virtual: {} {}".format(id, names))

    def on_install_clicked(self, btn, udata=None):
        """ User clicked install """
        self.context.begin_install(self.item)

    def on_remove_clicked(self, btn, udata=None):
        """ User clicked remove """
        self.context.begin_remove(self.item)

    def on_launch_clicked(self, btn, udata=None):
        """ User clicked launch """
        self.launch_info.launch(None, None)
