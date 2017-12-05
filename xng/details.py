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

from gi.repository import Gtk
from .screenshot_view import ScScreenshotView
from .util.markdown import SpecialMarkdownParser
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
    header_action = None

    stack = None
    stack_switcher = None

    screenie_view = None

    # We actually put lots of labels in this guy.
    description_box = None
    parser = None

    def get_page_name(self):
        return "{} - Software Center".format(self.header_name.get_text())

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

        self.item = item

        # Grab the app
        apps = self.context.appsystem
        id = item.get_id()

        # Update main header
        self.header_name.set_markup(apps.get_name(id, item.get_name()))
        self.header_summary.set_markup(
            apps.get_summary(id, item.get_summary()))
        pbuf = apps.get_pixbuf_only(id)
        self.header_image.set_from_pixbuf(pbuf)

        # Now set the screenshot ball in motion
        self.screenie_view.set_item(item)

        self.update_description()

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

        # actions
        self.header_action = Gtk.Button("Install")
        self.header_action.set_valign(Gtk.Align.CENTER)
        box.pack_end(self.header_action, False, False, 0)

        self.stack = Gtk.Stack()
        self.stack.set_homogeneous(False)
        self.stack_switcher = Gtk.StackSwitcher()
        self.stack_switcher.set_halign(Gtk.Align.CENTER)
        self.stack_switcher.set_stack(self.stack)
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
        desc = self.context.appsystem.get_description(id, fallback)

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
