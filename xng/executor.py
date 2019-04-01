#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017-2019 Solus
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#


from .op_queue import OperationQueue, Operation, OperationType
from gi.repository import GObject, Gdk, GLib, Notify
from threading import Lock, Thread


class Executor(GObject.Object):
    """ Executor is responsible for handling the main "loop" around the
        installation/removal of packages
    """

    queue = None
    thread_lock = None
    thread_running = False

    progress_string = None
    progress_value = None
    job_description = None
    notification = None
    context = None

    __gtype_name__ = "ScExecutor"

    __gsignals__ = {
        'execution-started': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'execution-ended': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'refreshed': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, ()),
        'job-enqueued': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,
                         (Operation,)),
        'job-dequeued': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE,
                         (Operation,))
    }

    def __init__(self, context):
        GObject.Object.__init__(self)
        self.context = context

        self.progress_value = 0.0
        # Management of the work queue
        self.queue = OperationQueue()
        self.thread_lock = Lock()
        self.thread_running = False

    def set_progress_string(self, msg):
        """ Update the progress message to be displayed for the ongoing
            actions

            This should be called by the backend being executed
        """
        Gdk.threads_enter()
        self.progress_string = msg
        print(msg)
        Gdk.threads_leave()

    def get_progress_string(self):
        return self.progress_string

    def get_progress_value(self):
        return self.progress_value

    def set_progress_value(self, value):
        """ Set the current progress value that will be displayed

            This should be called by the backend being executed
        """
        Gdk.threads_enter()
        self.progress_value = value
        print(value)
        Gdk.threads_leave()

    def get_job_description(self):
        return self.job_description

    def emit_enqueued(self, operation):
        """ Let folks know a new job is enqueued """
        self.emit('job-enqueued', operation)

    def emit_dequeued(self, operation):
        """ Let folks know a job has been dequeued """
        self.emit('job-dequeued', operation)

    def push_operation(self, operation):
        """ Push an operation and mark it queued """
        self.emit_enqueued(operation)
        self.queue.push_operation(operation)
        self.maybe_respawn()

    def install_package(self, ids):
        """ Install or queue installation """
        self.push_operation(Operation.Install(ids))

    def remove_package(self, ids):
        """ Remove or queue removal """
        self.push_operation(Operation.Remove(ids))

    def upgrade_package(self, ids):
        """ Upgrade or queue upgrade """
        self.push_operation(Operation.Upgrade(ids))

    def refresh_source(self, source):
        """ Push a refresh operation onto the queue """
        self.push_operation(Operation.Refresh(source))

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
                self.emit_dequeued(item)
                self.set_job_description(item)
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

    def set_job_description(self, item):
        """ Set appropriate job description for sidebar display """
        self.job_description = GLib.markup_escape_text(str(item.describe()))
        # Update our initial display label
        self.progress_string = "{}…".format(_("Waiting"))

    def process_queue_item(self, item):
        """ Handle execution of a single item """
        plugin = item.data.get_plugin()
        # Process
        if item.opType == OperationType.INSTALL:
            plugin.install_item(self, item.data)
        elif item.opType == OperationType.REMOVE:
            plugin.remove_item(self, item.data)
        elif item.opType == OperationType.UPGRADE:
            plugin.remove_item(self, item.data)
        elif item.opType == OperationType.REFRESH:
            plugin.refresh_source(self, item.data)

    def begin_executor_busy(self, item):
        """ Let listeners know the executor is stepping into a job now """
        Gdk.threads_enter()
        self.emit('execution-started')
        Gdk.threads_leave()

    def end_executor_busy(self, item):
        """ Let listeners know we're done for now """
        Gdk.threads_enter()
        self.emit('execution-ended')
        if item.opType == OperationType.REFRESH:
            self.emit('refreshed')
        else:
            self.notify_ended(item)
        Gdk.threads_leave()

    def get_item_name(self, item):
        """ Get the nice name for the item """
        id = item.get_id()
        app_name = self.context.appsystem.get_name(id, item.get_name())
        return GLib.markup_escape_text(str(app_name))

    def notify_ended(self, item):
        """ Send a notification to indicate job ending """
        icon_name = "system-software-install"
        body = None
        title = None
        if item.opType == OperationType.INSTALL:
            name = self.get_item_name(item.data.primary_item)
            title = _("New software installed")
            body = _("Installed {}").format(name)
        elif item.opType == OperationType.REMOVE:
            name = self.get_item_name(item.data.primary_item)
            title = _("Software removed")
            body = _("Removed {}").format(name)
        elif item.opType == OperationType.UPGRADE:
            title = _("Software update completed")
            body = _("Software updates have been completed")
        else:
            return

        if not self.notification:
            self.notification = Notify.Notification.new(title, body, icon_name)
        else:
            self.notification.update(title, body, icon_name)
        self.notification.set_timeout(4000)
        self.notification.show()
