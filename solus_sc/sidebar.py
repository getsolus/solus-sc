#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2020 Solus
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk


class ScSidebar(Gtk.ListBox):

    parent_stack = None
    first_real_show = False
    size_group = None
    owner = None

    def on_row_selected(self, us, udata=None):
        """ Handle navigation for the primary view """
        row = self.get_selected_row()
        if not row:
            return

        # Don't interrupt the first animation
        if not self.first_real_show:
            typ = Gtk.StackTransitionType.SLIDE_UP_DOWN
            self.parent_stack.set_transition_type(typ)
            self.first_real_show = True

        child = row.get_child()
        self.parent_stack.set_visible_child_name(child.row_entry)
        if child.row_entry == "search":
            self.parent_stack.get_child_by_name("search").handle_focus()
        self.owner.update_back(child.row_entry)

    def preselect_row(self, nom):
        """ Select the named row consistently """
        for row in self.get_children():
            child = row.get_child()
            if child.row_entry == nom:
                self.select_row(row)
                self.queue_draw()
                break

    def __init__(self, owner, parent_stack):
        Gtk.ListBox.__init__(self)

        self.set_can_focus(False)
        self.owner = owner

        self.get_style_context().add_class(Gtk.STYLE_CLASS_SIDEBAR)
        self.get_style_context().add_class(Gtk.STYLE_CLASS_VIEW)
        self.size_group = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        self.parent_stack = parent_stack
        self.get_style_context().add_class("main-sidebar")
        self.set_property("width-request", 160)

        icon_theme = self.get_settings().get_property("gtk-icon-theme-name")
        icon_theme = icon_theme.lower().replace("-", "")

        if "breeze" in icon_theme:
            update_icon = "arrow-up"
        else:
            update_icon = "software-update-available-symbolic"

        items = [
            ("home", _("Home"), "user-home-symbolic"),
            ("updates", _("Updates"), update_icon),
            ("installed", _("Installed"), "computer-symbolic"),
            ("3rd-party", _("Third Party"), "folder-download-symbolic"),
            ("search", _("Search"), "edit-find-symbolic"),
            ("settings", _("Settings"), "system-run-symbolic"),
        ]

        sel = None
        for item, label_sz, icon_sz in items:
            row = Gtk.HBox(0)
            label = Gtk.Label(label_sz)

            image = Gtk.Image.new_from_icon_name(icon_sz,
                                                 Gtk.IconSize.SMALL_TOOLBAR)
            row.pack_start(image, False, False, 0)
            image.set_property("margin-start", 10)
            image.set_property("margin-end", 10)
            label.set_property("margin-end", 15)
            row.pack_start(label, True, True, 0)
            row.row_entry = item
            label.set_halign(Gtk.Align.START)

            self.size_group.add_widget(label)
            # SizeGroup alignment "unfinished" since birth of iron age.
            label.set_alignment(0.0, 0.5)

            if sel is None:
                sel = row

            label.set_can_focus(False)
            self.add(row)
            label.get_parent().set_can_focus(False)

        self.select_row(sel.get_parent())
        self.connect("row-selected", self.on_row_selected)
