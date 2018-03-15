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

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.set_size_request(200, -1)

        self.context = context
        sep = Gtk.Separator.new(Gtk.Orientation.HORIZONTAL)
        sep.set_margin_top(6)
        sep.set_margin_bottom(18)
        self.pack_start(sep, False, False, 0)

        # Ongoing jobs
        lab = self.fancy_header(_("Tasks"), "system-run")
        self.pack_start(lab, False, False, 0)
        lab.set_margin_bottom(20)

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

        # Primary running job is a dynamic ScJobWidget
        self.running_job = ScJobWidget(True)
        self.listbox_jobs.add(self.running_job)

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
