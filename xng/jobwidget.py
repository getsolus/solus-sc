#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2020 Solus
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk, GLib


class ScJobWidget(Gtk.Box):
    """ Provide a simple widget to provide information about jobs.
        Typically a JobWidget does nothing but show static information,
        however a special case instance is preserved forever to simplify
        updating the *current* job information
    """

    __gtype_name__ = "ScJobWidget"

    title_label = None
    action_label = None
    progressbar = None
    size_group = None

    context = None
    monitor_id = None

    def __init__(self, context=None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.set_spacing(3)
        self.set_property("margin", 4)

        self.size_group = Gtk.SizeGroup.new(Gtk.SizeGroupMode.HORIZONTAL)

        # Construct our title label.
        self.title_label = Gtk.Label.new("<small>{}</small>".format(
            "Update system software"))
        self.title_label.set_halign(Gtk.Align.START)
        self.title_label.set_property("xalign", 0.0)
        self.title_label.set_use_markup(True)
        self.pack_start(self.title_label, False, False, 0)
        self.size_group.add_widget(self.title_label)

        self.context = context
        # No sense in creating widgets we never use.
        if not self.context:
            return

        # Construct our ongoing action label
        self.action_label = Gtk.Label.new("<small>{}</small>".format(
            "Applying operation 25/50"))
        self.action_label.set_halign(Gtk.Align.START)
        self.action_label.set_property("xalign", 0.0)
        self.action_label.set_use_markup(True)
        self.action_label.get_style_context().add_class("dim-label")
        self.pack_start(self.action_label, False, False, 0)
        self.size_group.add_widget(self.action_label)

        # Construct our progress widget
        self.progressbar = Gtk.ProgressBar.new()
        self.progressbar.set_margin_top(2)
        self.progressbar.set_fraction(0.5)
        self.progressbar.set_halign(Gtk.Align.START)
        self.pack_start(self.progressbar, False, False, 0)
        self.size_group.add_widget(self.progressbar)

        # Make sure we know what the context is doing
        self.context.executor.connect('execution-started', self.start_exec)
        self.context.executor.connect('execution-ended', self.end_exec)

    def start_exec(self, executor):
        """ Executor started a job, start monitoring now """
        # Stop existing monitor
        if self.monitor_id is not None:
            print("Removing old monitor")
            GLib.source_remove(self.monitor_id)
            self.monitor_id = None

        # Give us an appropriate display label
        self.title_label.set_markup("<small>{}</small>".format(
            self.context.executor.get_job_description()))

        # Set up new monitor
        print("Adding new monitor")
        self.monitor_id = GLib.timeout_add(50, self.monitor_callback)

    def end_exec(self, executor):
        """ Executor ended a job, stop monitoring now """
        if self.monitor_id is not None:
            print("Stopped old monitor")
            GLib.source_remove(self.monitor_id)
            self.monitor_id = None
        pass

    def monitor_callback(self):
        """ Idle timer to routinely update our state """
        self.action_label.set_markup("<small>{}</small>".format(
            self.context.executor.get_progress_string()))
        self.progressbar.set_fraction(
            self.context.executor.get_progress_value())
        return self.monitor_id is not None

    def update_job(self, job):
        """ Update our appearance based on a pending job """
        safe = GLib.markup_escape_text(job.describe())
        self.title_label.set_markup("<small>{}</small>".format(safe))
