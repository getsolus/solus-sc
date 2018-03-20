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


from .op_queue import OperationQueue, Operation, OperationType
from gi.repository import GObject
from threading import Lock, Thread
from .plugins.base import ProviderItem


class Executor(GObject.Object):
    """ Executor is responsible for handling the main "loop" around the
        installation/removal of packages
    """

    queue = None
    thread_lock = None
    thread_running = False

    progress_string = None
    progress_value = None

    __gtype_name__ = "ScExecutor"

    __gsignals__ = {
        'execution-started': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                              (ProviderItem,)),
        'execution-ended': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                            (ProviderItem,))
    }

    def __init__(self):
        GObject.Object.__init__(self)

        # Management of the work queue
        self.queue = OperationQueue()
        self.thread_lock = Lock()
        self.thread_running = False

    def set_progress_string(self, msg):
        """ Update the progress message to be displayed for the ongoing
            actions

            This should be called by the backend being executed
        """
        self.progress_string = msg

    def set_progress_value(self, value):
        """ Set the current progress value that will be displayed

            This should be called by the backend being executed
        """
        self.progress_value = value

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
            try:
                self.begin_executor_busy(item)
                self.process_queue_item(item)
            finally:
                self.end_executor_busy(item)

        # Queue ran out
        print("queue emptied")
        self.thread_lock.acquire()
        try:
            self.thread_running = False
        finally:
            self.thread_lock.release()

    def process_queue_item(self, item):
        """ Handle execution of a single item """
        plugin = item.data.get_plugin()
        # Process
        if item.opType == OperationType.INSTALL:
            plugin.install_item((item.data, ))
        elif item.opType == OperationType.REMOVE:
            plugin.install_item(item.data)
        elif item.opType == OperationType.UPGRADE:
                plugin.remove_item(item.data)

    def begin_executor_busy(self, item):
        """ Let listeners know the executor is stepping into a job now """
        self.emit('execution-started', item.data)

    def end_executor_busy(self, item):
        """ Let listeners know we're done for now """
        self.emit('execution-ended', item.data)
