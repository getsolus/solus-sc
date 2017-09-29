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


from .op_queue import OperationQueue, Operation, OperationType
from threading import Lock, Thread

class Executor:
    """ Executor is responsible for handling the main "loop" around the
        installation/removal of packages
    """

    queue = None
    thread_lock = None
    thread_running = False

    def __init__(self):
        self.queue = OperationQueue()
        self.thread_lock = Lock()
        self.thread_running = False

        # TODO: Spawn a thread

    def install_package(self, ids):
        """ Install or queue installation """
        self.queue.push_operation(Operation.Install(ids))
        self.maybe_respawn()

    def remove_package(self, ids):
        """ Remove or queue removal """
        self.queue.push_operation(Operation.Remove(ids))
        self.maybe_respawn()

    def upgrade_package(self, ids):
        """ Upgrade or queue upgrade """
        self.queue.push_operation(Operation.Upgrade(ids))
        self.maybe_respawn()

    def maybe_respawn(self):
        """ Start up the worker thread again if our thread ended """
        self.thread_lock.acquire()
        try:
            if not self.thread_running:
                self.thread_running = True
                print("debug: spawning new work thread")
                t = Thread(target=self.process_queue)
                t.start()
            else:
                print("debug: thread is already running")
        finally:
            self.thread_lock.release()

    def process_queue(self):
        """ Process the queue until it empties """
        while not self.queue.opstack.empty():
            item = self.queue.opstack.get()
            plugin = item.data.get_plugin()
            if item.opType == OperationType.INSTALL:
                plugin.install_item(item.data)
            elif item.opType == OperationType.REMOVE:
                plugin.install_item(item.data)
            elif item.opType == OperationType.UPGRADE:
                plugin.remove_item(item.data)
            print("Got item: {}".format(item.data))
        # Queue ran out
        print("queue emptied")
        self.thread_lock.acquire()
        try:
            self.thread_running = False
        finally:
            self.thread_lock.release()
