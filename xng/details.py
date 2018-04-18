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

from gi.repository import Gio, Gtk
from .screenshot_view import ScScreenshotView
from .util.markdown import SpecialMarkdownParser
from .plugins.base import ItemStatus
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
        pbuf = apps.get_pixbuf_only(id, store)
        self.header_image.set_from_pixbuf(pbuf)

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
        self.stack_switcher.set_halign(Gtk.Align.CENTER)
        self.stack_switcher.set_stack(self.stack)
        self.stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        box_main_wrap.pack_start(self.stack_switcher, False, False, 0)
        self.pack_start(self.stack, True, True, 0)

        # Dummy pages for now
        self.build_details()
        self.stack.add_titled(Gtk.Box(), "changelog", "Changelog")

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

        # A place to have our description
        self.description_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.description_box.set_margin_top(30)
        self.description_box.set_margin_end(150)
        self.description_box.set_margin_start(30)
        box.pack_start(self.description_box, False, False, 0)

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

    def on_install_clicked(self, btn, udata=None):
        """ User clicked install """
        self.context.begin_install(self.item)

    def on_remove_clicked(self, btn, udata=None):
        """ User clicked remove """
        self.context.begin_remove(self.item)

    def on_launch_clicked(self, btn, udata=None):
        """ User clicked launch """
        self.launch_info.launch(None, None)
