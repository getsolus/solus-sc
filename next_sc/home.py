#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk
from plugins.base import PopulationFilter

class HomeView(Gtk.Box):

    # Our next_sc plugin set
    plugins = None

    # Our appsystem for resolving metadata
    appsystem = None

    box_new = None
    box_recent = None

    def __init__(self, appsystem, plugins):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.appsystem = appsystem
        self.plugins = plugins

        lab = Gtk.Label.new("<big>{}</big>".format(_("New software")))
        lab.set_margin_start(6)
        lab.set_margin_top(6)
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.START)
        self.pack_start(lab, False, False, 0)
        self.box_new = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.box_new.set_margin_bottom(12)
        self.pack_start(self.box_new, False, False, 0)

        lab = Gtk.Label.new("<big>{}</big>".format(_("Recently updated")))
        lab.set_margin_start(6)
        lab.set_margin_top(6)
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.START)
        self.pack_start(lab, False, False, 0)
        self.box_recent = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.pack_start(self.box_recent, False, False, 0)

        # find out about new shinies
        for p in self.plugins:
            p.populate_storage(self, PopulationFilter.INSTALLED, self.appsystem)
            p.populate_storage(self, PopulationFilter.RECENT, self.appsystem)

    def clear(self):
        """ Clear any custom stuff from the home view """
        for child in box_new.get_children():
            child.destroy()
        for child in box_recent.get_children():
            child.destroy()

    def add_item(self, id, item, popfilter):
        """ Handle adding items to our view """
        target = None
        if popfilter == PopulationFilter.NEW:
            target = self.box_new
        elif popfilter == PopulationFilter.RECENT:
            target = self.box_recent
        else:
            return

        pbuf = self.appsystem.get_pixbuf(id)
        img = Gtk.Image.new_from_pixbuf(pbuf)
        img.set_margin_end(8)
        btnText = self.appsystem.get_name(id, item.get_title())
        summary = self.appsystem.get_summary(id, item.get_summary())
        if len(summary) > 40:
            summary = "%s…" % summary[0:40]
        btnText = "<b>{}</b>\n{}".format(btnText, summary)
        btn = Gtk.Button.new()
        btn.get_style_context().add_class("flat")
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.pack_start(img, False, False, 0)
        lab = Gtk.Label.new(btnText)
        lab.set_use_markup(True)
        box.pack_start(lab, True, True, 0)
        btn.add(box)
        btn.show_all()
        btn.set_margin_start(6)
        btn.set_margin_end(6)
        target.pack_start(btn, False, False, 0)
