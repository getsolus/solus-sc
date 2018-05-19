#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

import Queue

from gi.repository import GObject


class OperationType:

    INSTALL = 3  # Installs should be evaluated after removals
    REMOVE = 2   # Remove is low-ish priority but must be before installs
    UPGRADE = 1  # Upgrades should be before anything changing packages
    REFRESH = 0  # Refresh is highest priority


class Operation(GObject.Object):
    """ Operation wraps up various operations so that they can be applied
        immediately whilst other operations will continue to be stacked up
        until such time as they can be applied.
    """

    opType = 0
    data = None

    __gtype_name__ = "XngOperation"

    def __cmp__(self, other):
        """ Ensure we can make other items higher priority ... """
        return cmp(self.opType, other.opType)

    def __init__(self, data, opType):
        GObject.Object.__init__(self)
        self.data = data
        self.opType = opType

    def describe(self):
        """ Describe the current job/operation """
        return self.data.describe()
        name = self.data.get_name()
        if self.opType == OperationType.INSTALL:
            # Install 'gedit'
            return _("Install '{}'".format(name))
        elif self.opType == OperationType.REMOVE:
            # Remove 'gedit'
            return _("Remove '{}'".format(name))
        elif self.opType == OperationType.REFRESH:
            # Refresh source 'Solus'
            return _("Refresh source '{}'".format(name))
        else:
            # Don't know how to handle update yet
            return None

    @staticmethod
    def Install(ids):
        return Operation(ids, OperationType.INSTALL)

    @staticmethod
    def Remove(ids):
        return Operation(ids, OperationType.REMOVE)

    @staticmethod
    def Upgrade(ids):
        return Operation(ids, OperationType.UPGRADE)

    @staticmethod
    def Refresh(source):
        return Operation(source, OperationType.REFRESH)


class OperationQueue:
    """ OperationQueue is used to apply any pending packaging operations
        within the Software Center one after another
    """

    # We enqueue pending operations here
    opstack = None

    def __init__(self):
        self.opstack = Queue.PriorityQueue(0)

    def push_operation(self, op):
        """ Set up an operation to be applied """
        self.opstack.put(op)
