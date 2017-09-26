#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#


from .op_queue import OperationQueue, Operation

class Executor:
    """ Executor is responsible for handling the main "loop" around the
        installation/removal of packages
    """

    queue = None

    def __init__(self):
        self.queue = OperationQueue()

        # TODO: Spawn a thread

    def install_package(self, ids):
        """ Install or queue installation """
        self.queue.push_operation(Operation.Install(ids))

    def remove_package(self, ids):
        """ Remove or queue removal """
        self.queue.push_operation(Operation.Remove(ids))

    def upgrade_package(self, ids):
        """ Upgrade or queue upgrade """
        self.queue.push_operation(Operation.Upgrade(ids))
