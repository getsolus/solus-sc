#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk


class ScFeaturedPage(Gtk.Box):
    """ Single page in a featured stack """

    context = None
    item = None

    def __init__(self, context, item):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.set_halign(Gtk.Align.CENTER)

        self.context = context
        self.item = item
        id = self.item.get_id()

        image = self.context.appsystem.get_pixbuf_massive(id)

        self.image = Gtk.Image.new_from_pixbuf(image)
        self.image.set_halign(Gtk.Align.START)
        self.image.set_valign(Gtk.Align.START)
        self.image.set_margin_end(48)
        self.pack_start(self.image, False, False, 0)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.pack_start(box, False, False, 0)

        txt = self.context.appsystem.get_name(id, item.get_name())
        lab = Gtk.Label(txt)
        lab.get_style_context().add_class("huge-label")
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.START)
        lab.set_valign(Gtk.Align.START)
        box.pack_start(lab, False, False, 0)

        desc = self.context.appsystem.get_summary(id, item.get_summary())
        lab = Gtk.Label(desc)
        lab.get_style_context().add_class("desc-label")
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.START)
        lab.set_valign(Gtk.Align.START)
        box.pack_start(lab, False, False, 0)


class ScFeatured(Gtk.EventBox):
    """ Experiment to create a "Featured" view """

    stack = None
    pages = []
    dots = []
    idx = 0

    def __init__(self, context):
        Gtk.EventBox.__init__(self)
        self.context = context
        self.overlay = Gtk.Overlay()
        self.add(self.overlay)
        self.get_style_context().add_class("featured-box")
        self.get_style_context().add_class("content-view")

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.main_layout = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.vbox.pack_start(self.main_layout, True, True, 0)

        self.overlay.add(self.vbox)
        self.overlay.set_property("margin", 12)

        buttons = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.overlay.add_overlay(buttons)

        button_back = Gtk.Button.new_from_icon_name(
            "go-previous-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
        button_next = Gtk.Button.new_from_icon_name(
            "go-next-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
        button_back.connect("clicked", self.do_back)
        button_next.connect("clicked", self.do_next)

        button_back.get_style_context().add_class("image-button")
        button_back.get_style_context().add_class("osd")
        button_back.get_style_context().add_class("round-button")

        button_next.get_style_context().add_class("image-button")
        button_next.get_style_context().add_class("osd")
        button_next.get_style_context().add_class("round-button")

        buttons.pack_start(button_back, False, False, 0)
        buttons.pack_end(button_next, False, False, 0)
        buttons.set_halign(Gtk.Align.FILL)
        buttons.set_valign(Gtk.Align.CENTER)
        buttons.set_border_width(8)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(
            Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.vbox.pack_start(self.stack, False, False, 0)

        self.thumbs = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.thumbs.set_halign(Gtk.Align.CENTER)
        self.thumbs.set_margin_top(12)
        self.thumbs.set_margin_bottom(12)
        self.vbox.pack_start(self.thumbs, False, False, 0)
        self.thumbs.set_halign(Gtk.Align.CENTER)

    def add_item(self, id, item, popfilter):
        """ Implement the population storage API """
        thumb = Gtk.Label("•")
        thumb.get_style_context().add_class("big-thumb")
        thumb.get_style_context().add_class("dim")
        self.thumbs.pack_start(thumb, False, False, 0)
        thumb.show_all()

        page = ScFeaturedPage(self.context, item)
        self.stack.add_named(page, item.get_id())
        page.show_all()
        self.pages.append(page)
        self.dots.append(thumb)
        self.navigate(0)

    def do_next(self, btn, data=None):
        self.navigate(+1)

    def do_back(self, btn, data=None):
        self.navigate(-1)

    def navigate(self, incr):
        """ Wrap any navigation as necessary """
        idx = (self.idx + incr) % (len(self.pages))
        self.dots[self.idx].get_style_context().add_class("dim")
        self.dots[idx].get_style_context().remove_class("dim")
        self.stack.set_visible_child(self.pages[idx])
        self.idx = idx
