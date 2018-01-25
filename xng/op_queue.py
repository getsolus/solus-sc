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


class OperationType:

    INSTALL = 2  # Installs should be evaluated after removals
    REMOVE = 1   # Remove is low-ish priority but must be before installs
    UPGRADE = 0  # Upgrades should be before everything!


class Operation:
    """ Operation wraps up various operations so that they can be applied
        immediately whilst other operations will continue to be stacked up
        until such time as they can be applied.
    """

    opType = 0
    data = None

    def __cmp__(self, other):
        """ Ensure we can make other items higher priority ... """
        return cmp(self.opType, other.opType)

    def __init__(self, data, opType):
        self.data = data
        self.opType = opType

    @staticmethod
    def Install(ids):
        return Operation(ids, OperationType.INSTALL)

    @staticmethod
    def Remove(ids):
        return Operation(ids, OperationType.REMOVE)

    @staticmethod
    def Upgrade(ids):
        return Operation(ids, OperationType.UPGRADE)


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
