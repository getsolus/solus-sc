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

from gi.repository import Gtk, Gdk
import threading
from .op_queue import OperationType


class ScOperationDialog(Gtk.Dialog):
    """ Shows details about an install/remove operation before doing it.

        The details view is effectively the pretty view with all the relevant
        package/software details, screenshots, and actions to invoke removal,
        installation, etc.
    """

    __gtype_name__ = "ScOperationDialog"

    item = None  # Currently active item for planning
    operation_type = None  # Currently requested operation type

    def __init__(self, window):
        Gtk.Dialog.__init__(self, transient_for=window, use_header_bar=1)

    def prepare(self, item, operation_type):
        """ Prepare to be shown on screen """
        self.item = item
        self.operation_type = operation_type
        thr = threading.Thread(target=self.begin_operation)

        # mark title according to request
        if self.operation_type == OperationType.INSTALL:
            self.set_title(_("Install software"))
        elif self.operation_type == OperationType.REMOVE:
            self.set_title(_("Remove software"))
        elif self.operation_type == OperationType.UPGRADE:
            self.set_title(_("Upgrade software"))

        self.show_all()
        self.begin_busy()

        # Start the operation calculation
        thr.start()

    def begin_busy(self):
        """ Mark ourselves busy before we do anything... """
        self.set_sensitive(False)

    def end_busy(self):
        """" We're now now ready to be used ... """
        self.set_sensitive(True)

    def begin_operation(self):
        """ Here we begin the actual planning for this dialog... """
        # Get this dude in a second
        transaction = None
        plugin = self.item.get_plugin()

        if self.operation_type == OperationType.INSTALL:
            transaction = plugin.plan_install_item(self.item)
        elif self.operation_type == OperationType.REMOVE:
            transaction = plugin.plan_remove_item(self.item)
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
        self.end_busy()
        Gdk.threads_leave()
