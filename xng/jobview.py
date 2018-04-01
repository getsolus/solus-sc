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

from gi.repository import Gtk

from .jobwidget import ScJobWidget


class ScJobView(Gtk.Box):
    """ Provide a view to show ongoing and enqueued jobs
    """

    __gtype_name__ = "ScJobView"

    context = None

    running_job = None
    listbox_jobs = None

    runner_stack = None  # Allow switching between running/not-running

    jobs = None  # Mapping of jobs

    pending_revealer = None

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.set_size_request(200, -1)

        self.context = context
        # Need to know all the jobs
        self.context.executor.connect('execution-started', self.start_exec)
        self.context.executor.connect('execution-ended', self.end_exec)
        self.jobs = dict()
        self.context.executor.connect('job-enqueued', self.job_enqueued)
        self.context.executor.connect('job-dequeued', self.job_dequeued)

        # Ongoing jobs
        lab = self.fancy_header(_("Tasks"), "view-list-symbolic")
        self.pack_start(lab, False, False, 0)
        lab.set_margin_start(4)
        lab.set_margin_bottom(20)

        self.build_primary_job()

        # Pending tasks
        self.pending_revealer = Gtk.Revealer.new()
        self.pending_revealer.set_transition_type(
            Gtk.RevealerTransitionType.SLIDE_UP)
        lab = Gtk.Label("<small>{}</small>".format(_("Queued tasks")))
        lab.get_style_context().add_class("dim-label")
        lab.set_use_markup(True)
        self.pending_revealer.add(lab)
        lab.set_margin_start(4)
        lab.set_margin_top(6)
        lab.set_margin_bottom(6)
        lab.set_halign(Gtk.Align.START)
        self.pending_revealer.set_reveal_child(False)
        self.pack_start(self.pending_revealer, False, False, 0)

        # Create our fancyish listbox
        self.listbox_jobs = Gtk.ListBox.new()
        self.listbox_jobs.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll = Gtk.ScrolledWindow.new(None, None)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.listbox_jobs)
        scroll.set_valign(Gtk.Align.FILL)
        self.listbox_jobs.set_valign(Gtk.Align.FILL)
        self.listbox_jobs.set_vexpand(True)
        scroll.set_shadow_type(Gtk.ShadowType.NONE)
        self.pack_start(scroll, True, True, 0)

    def build_primary_job(self):
        """ Build the primary "running job" view """
        self.running_job = ScJobWidget(self.context)

        # Build runner stack to allow switching out to no active jobs
        self.runner_stack = Gtk.Stack.new()
        self.runner_stack.set_transition_type(
            Gtk.StackTransitionType.CROSSFADE)
        self.pack_start(self.runner_stack, False, False, 0)
        self.runner_stack.set_interpolate_size(True)

        # Not running job
        lab = Gtk.Label.new("<small>{}</small>".format(
            _("No currently running tasks")))
        lab.set_use_markup(True)
        lab.get_style_context().add_class("dim-label")
        lab.set_halign(Gtk.Align.START)
        lab.set_margin_start(4)
        lab.set_valign(Gtk.Align.CENTER)
        self.runner_stack.add_named(lab, 'not-running')

        # Running job
        self.runner_stack.add_named(self.running_job, 'running')
        self.runner_stack.set_visible_child_name('not-running')

    def fancy_header(self, title, icon):
        """ Build a fancy consistent header for the top section """
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        lab = Gtk.Label.new(title)
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.START)
        img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.SMALL_TOOLBAR)
        img.set_margin_end(6)

        box.pack_start(img, False, False, 0)
        box.pack_start(lab, False, False, 0)
        box.set_margin_top(6)
        box.set_margin_bottom(6)
        return box

    def start_exec(self, executor):
        """ Show the job widget again """
        self.runner_stack.set_visible_child_name('running')

    def end_exec(self, executor):
        """ Hide job widget again """
        self.runner_stack.set_visible_child_name('not-running')

    def job_enqueued(self, executor, job):
        """ Add a new job representation """
        if job in self.jobs:
            return
        wid = ScJobWidget()
        wid.update_job(job)
        wid.show_all()
        self.listbox_jobs.add(wid)
        self.jobs[job] = wid
        self.pending_revealer.set_reveal_child(True)

    def job_dequeued(self, executor, job):
        """ Remove our job representation """
        if job not in self.jobs:
            return
        jobview = self.jobs[job]
        self.listbox_jobs.remove(jobview.get_parent())
        del self.jobs[job]
        if len(self.jobs) < 1:
            self.pending_revealer.set_reveal_child(False)
