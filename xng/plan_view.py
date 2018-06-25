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

from gi.repository import Gtk, Gdk, GLib
import threading
from .op_queue import OperationType


class ScExtraItem(Gtk.ListBoxRow):
    """ Utility class to encapsulate items for display in boxes """

    __gtype_name__ = "ScExtraItem"

    name = None

    def __init__(self, context, item):
        Gtk.ListBoxRow.__init__(self)
        self.label = Gtk.Label.new("")
        self.add(self.label)

        self.label.set_halign(Gtk.Align.START)
        self.label.set_use_markup(False)

        # Stash for enquiry
        id = item.get_id()
        store = item.get_store()

        # Get clean name
        name = context.appsystem.get_name(id, item.get_name(), store)
        self.name = GLib.markup_escape_text(name)
        self.label.set_markup("<small>{}</small>".format(self.name))
        self.show_all()


class ScExtrasBox(Gtk.Box):
    """ Simple composite widget containing a label and a listbox of items
        which show extra dependencies and such
    """""

    __gtype_name__ = "ScExtrasBox"

    context = None

    listbox_items = None
    label_header = None

    def __init__(self, context, title):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.context = context

        # Whack in the top label
        self.label_header = Gtk.Label.new(title)
        self.label_header.get_style_context().add_class("dim-label")
        self.label_header.set_halign(Gtk.Align.START)
        self.pack_start(self.label_header, False, False, 0)
        self.label_header.set_margin_bottom(6)

        # Scroller just prevents us getting ugly shadows.
        self.scroller = Gtk.ScrolledWindow.new(None, None)
        self.scroller.set_shadow_type(Gtk.ShadowType.NONE)
        self.scroller.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        self.pack_start(self.scroller, True, True, 0)

        # Listbox to store items lives inside the scrolledwindow
        self.listbox_items = Gtk.ListBox.new()
        self.listbox_items.set_sort_func(self.sort_items)
        self.listbox_items.set_selection_mode(Gtk.SelectionMode.NONE)
        self.scroller.add(self.listbox_items)

        self.set_margin_top(6)

        # Ensure we can easily be hidden from view
        self.show_all()
        self.set_no_show_all(True)

    def sort_items(self, itemA, itemB):
        """ Alpha-sort the listings """
        return cmp(itemA.name.lower(), itemB.name.lower())

    def populate_from_set(self, transaction_set):
        """ Populate our view from the given transaction set """
        for child in self.listbox_items.get_children():
            child.destroy()

        if len(transaction_set) < 1:
            self.hide()
            return

        # TODO: Populate rows properly, this is crappy demo code
        for item in transaction_set:
            lab = ScExtraItem(self.context, item)
            self.listbox_items.add(lab)

        self.show()


class ScPlanView(Gtk.Box):
    """ Shows details about an install/remove operation before doing it.
    """

    __gtype_name__ = "ScPlanView"

    item = None  # Currently active item for planning
    operation_type = None  # Currently requested operation type

    # Additional sections
    box_installs = None
    box_removals = None
    box_upgrades = None

    label_space_used = None
    label_space_freed = None

    button_accept = None  # Allow remove/install/etc

    body_pane = None
    scroller = None
    transaction = None

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.context = context
        self.set_border_width(10)

        # Sort out scroller for body pane scrolling
        self.scroller = Gtk.ScrolledWindow.new(None, None)
        self.scroller.set_overlay_scrolling(False)
        self.scroller.set_shadow_type(Gtk.ShadowType.NONE)
        self.scroller.set_policy(
            Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(self.scroller, True, True, 0)
        self.body_pane = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.scroller.add(self.body_pane)

        self.scroller.set_margin_top(24)
        self.scroller.set_margin_bottom(24)

        self.build_extras()
        self.build_footer()

    def build_footer(self):
        """ Build the primary header which is always visible """
        # Allow showing how much space is going to be used here
        self.label_space_used = Gtk.Label.new("")
        self.label_space_used.show_all()
        self.label_space_used.set_no_show_all(True)
        self.pack_start(self.label_space_used, False, False, 0)
        self.label_space_used.set_margin_bottom(6)
        self.label_space_used.set_halign(Gtk.Align.START)

        # Likewise for space freed
        self.label_space_freed = Gtk.Label.new("")
        self.label_space_freed.show_all()
        self.label_space_freed.set_no_show_all(True)
        self.pack_start(self.label_space_freed, False, False, 0)
        self.label_space_freed.set_margin_bottom(6)
        self.label_space_freed.set_halign(Gtk.Align.START)

        self.button_accept = Gtk.Button.new_with_label(_("Accept changes"))
        self.button_accept.get_style_context().add_class("suggested-action")
        self.button_accept.set_halign(Gtk.Align.CENTER)
        self.pack_start(self.button_accept, False, False, 0)

        # Permanent padding
        self.button_accept.set_margin_top(24)
        self.button_accept.set_margin_bottom(24)

        # Ensure we have a wide view always
        self.button_accept.set_margin_start(48)
        self.button_accept.set_margin_end(48)

        # Hook this fella up.
        self.button_accept.connect('clicked', self.on_accept_clicked)

    def on_accept_clicked(self, widg, udata=None):
        """ Push the transaction back to whence it came """
        if not self.transaction:
            print("!!! DAFUQ. NO TRANSACTION !!!")
            return

        # Off it goes.
        self.context.execute_transaction(
            self.transaction, self.operation_type)

    def build_extras(self):
        """ Build sections for each of the 'extras' boxes to go """
        self.box_installs = ScExtrasBox(
            self.context,
            _("To be installed"))

        self.body_pane.pack_start(self.box_installs, False, False, 0)

        self.box_removals = ScExtrasBox(
            self.context,
            _("To be removed"))

        self.body_pane.pack_start(self.box_removals, False, False, 0)

        self.box_upgrades = ScExtrasBox(
            self.context, _("To be upgraded"))

        self.body_pane.pack_start(self.box_upgrades, False, False, 0)

    def prepare(self, item, operation_type):
        """ Prepare to be shown on screen """
        self.item = item
        self.operation_type = operation_type
        thr = threading.Thread(target=self.begin_operation)

        # TODO: Enforce modality so we can't dismiss!
        self.context.set_window_busy(True)

        # Start the operation calculation
        thr.start()

    def begin_operation(self):
        """ Here we begin the actual planning for this dialog... """
        # Get this dude in a second
        transaction = None
        self.transaction = None
        plugin = self.item.get_plugin()

        if self.operation_type == OperationType.INSTALL:
            transaction = plugin.plan_install_item(self.item)
        elif self.operation_type == OperationType.REMOVE:
            transaction = plugin.plan_remove_item(self.item, automatic=True)
        elif self.operation_type == OperationType.UPGRADE:
            transaction = plugin.plan_upgrade_item(self.item)
        else:
            print("!!! UNSUPPORTED OPERATION !!!")
            return

        print(transaction.removals)
        print(transaction.installations)
        print(transaction.upgrades)

        # Set ourselves sensitive/usable again
        Gdk.threads_enter()
        self.context.set_window_busy(False)
        self.transaction = transaction

        # Update boxes based on operation set
        self.box_installs.populate_from_set(transaction.installations)
        self.box_removals.populate_from_set(transaction.removals)
        self.box_upgrades.populate_from_set(transaction.upgrades)

        # Show install size?
        if transaction.install_size > 0:
            install_size = transaction.get_install_size()
            self.label_space_used.set_markup(
                _("<small>Installation size: <b>{}</b></small>").format(
                    install_size))
            self.label_space_used.show()
        else:
            self.label_space_used.hide()

        # Show remove size?
        if transaction.remove_size > 0:
            remove_size = transaction.get_removal_size()
            self.label_space_freed.set_markup(
                _("<small>Disk space freed: <b>{}</b></small>").format(
                    remove_size))
            self.label_space_freed.show()
        else:
            self.label_space_freed.hide()

        # Get back out of ugly gdk lock land
        Gdk.threads_leave()
