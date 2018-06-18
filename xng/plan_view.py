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


class ScPlanView(Gtk.Box):
    """ Shows details about an install/remove operation before doing it.
    """

    __gtype_name__ = "ScPlanView"

    item = None  # Currently active item for planning
    operation_type = None  # Currently requested operation type

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)
        self.context = context

    def prepare(self, item, operation_type):
        """ Prepare to be shown on screen """
        return
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

        # self.begin_busy()

        # Start the operation calculation
        thr.start()


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

        print("Install size: {}".format(transaction.get_install_size()))
        print("Removal size: {}".format(transaction.get_removal_size()))

        # Set ourselves sensitive/usable again
        # Gdk.threads_enter()
        # self.end_busy()
        # Gdk.threads_leave()
