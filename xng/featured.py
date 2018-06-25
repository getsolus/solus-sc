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

from gi.repository import Gtk, GObject, Gdk
from .plugins.base import PopulationFilter, ProviderItem


class ScFeaturedPage(Gtk.Box):
    """ Single page in a featured stack """

    context = None
    item = None
    action_callout = None

    def __init__(self, context, item):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.set_halign(Gtk.Align.CENTER)

        self.context = context
        self.item = item
        id = self.item.get_id()

        self.image = Gtk.Image.new()
        self.context.appsystem.set_image_from_item(self.image, self.item, self.item.get_store(), 128)
        self.image.set_halign(Gtk.Align.START)
        self.image.set_valign(Gtk.Align.START)
        self.image.set_margin_end(36)
        self.image.set_margin_top(12)
        self.pack_start(self.image, False, False, 0)

        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.pack_start(box, False, False, 0)
        box.set_halign(Gtk.Align.START)

        txt = self.context.appsystem.get_name(id, item.get_name())
        lab = Gtk.Label(txt)
        lab.set_margin_start(12)
        lab.set_margin_top(12)
        lab.get_style_context().add_class("huge-label")
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.START)
        lab.set_valign(Gtk.Align.START)
        box.pack_start(lab, False, False, 0)

        desc = self.context.appsystem.get_summary(id, item.get_summary())
        lab = Gtk.Label(desc)
        lab.set_margin_start(12)
        lab.get_style_context().add_class("desc-label")
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.START)
        lab.set_valign(Gtk.Align.START)
        box.pack_start(lab, False, False, 0)

        self.action_callout = Gtk.Button("Read more")
        self.action_callout.set_valign(Gtk.Align.END)
        self.action_callout.set_halign(Gtk.Align.START)
        self.action_callout.set_margin_top(12)
        self.action_callout.get_style_context().add_class("flat")
        box.pack_start(self.action_callout, False, False, 0)


class ScFeaturedThumb(Gtk.EventBox):
    """ The dot thumb shown for navigation """

    __gtype_name__ = "ScFeaturedThumb"

    # Related page
    thumb_id = None
    thumb = None

    def __init__(self, thumb_id):
        Gtk.EventBox.__init__(self)
        self.set_property("margin", 0)
        self.set_border_width(0)
        self.thumb_id = thumb_id

        self.thumb = Gtk.Label("•")
        self.thumb.get_style_context().add_class("big-thumb")
        self.thumb.get_style_context().add_class("dim")
        self.add(self.thumb)

        self.connect('realize', self.on_realized)

    def on_realized(self, udata=None):
        display = Gdk.Display.get_default()
        curs = Gdk.Cursor.new_from_name(display, "pointer")
        self.get_window().set_cursor(curs)

    def set_dim(self, dim):
        """ Mark as dim or not """
        if dim:
            self.thumb.get_style_context().add_class("dim")
        else:
            self.thumb.get_style_context().remove_class("dim")


class ScFeatured(Gtk.EventBox):
    """ Experiment to create a "Featured" view """

    stack = None
    pages = []
    dots = []
    idx = 0

    __gtype_name__ = "ScFeatured"

    __gsignals__ = {
        'item-selected': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
                          (ProviderItem,))
    }

    def __init__(self, context):
        Gtk.EventBox.__init__(self)
        self.context = context
        self.get_style_context().add_class("featured-box")
        self.get_style_context().add_class("content-view")

        self.vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        self.main_layout = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.main_layout.set_margin_start(12)
        self.main_layout.set_margin_end(12)
        self.main_layout.set_margin_top(24)

        self.add(self.main_layout)

        button_back = Gtk.Button.new_from_icon_name(
            "go-previous-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
        button_next = Gtk.Button.new_from_icon_name(
            "go-next-symbolic", Gtk.IconSize.LARGE_TOOLBAR)
        button_back.connect("clicked", self.do_back)
        button_next.connect("clicked", self.do_next)

        button_back.set_valign(Gtk.Align.CENTER)
        button_back.set_can_focus(False)
        button_back.get_style_context().add_class("image-button")
        button_back.get_style_context().add_class("osd")
        button_back.get_style_context().add_class("round-button")

        button_next.set_valign(Gtk.Align.CENTER)
        button_next.set_can_focus(False)
        button_next.get_style_context().add_class("image-button")
        button_next.get_style_context().add_class("osd")
        button_next.get_style_context().add_class("round-button")

        self.main_layout.pack_start(button_back, False, False, 0)
        self.main_layout.pack_start(self.vbox, True, True, 0)
        self.main_layout.pack_end(button_next, False, False, 0)

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

        thumb = ScFeaturedThumb(len(self.pages))
        self.thumbs.pack_start(thumb, False, False, 0)
        thumb.show_all()
        thumb.connect("button-press-event", self.on_button_press_event)

        page = ScFeaturedPage(self.context, item)
        page.action_callout.connect("clicked", self.on_clicked)
        self.stack.add_named(page, item.get_id())
        page.show_all()
        if not page.get_realized():
            page.realize()
        page.set_size_request(-1, -1)
        self.pages.append(page)
        self.dots.append(thumb)
        self.navigate(0)

    def on_button_press_event(self, widget, udata=None):
        """ Handle pressing of the dot """
        self.navigate(widget.thumb_id - self.idx)
        return Gdk.EVENT_PROPAGATE

    def on_clicked(self, btn, data=None):
        # Emit click for the currently selected item
        page = self.stack.get_visible_child()
        self.emit('item-selected', page.item)

    def do_next(self, btn, data=None):
        self.navigate(+1)

    def do_back(self, btn, data=None):
        self.navigate(-1)

    def navigate(self, incr):
        """ Wrap any navigation as necessary """
        idx = (self.idx + incr) % (len(self.pages))
        self.dots[self.idx].set_dim(True)
        self.dots[idx].set_dim(False)
        self.stack.set_visible_child(self.pages[idx])
        self.idx = idx


class ScFeaturedEmbed(Gtk.Revealer):
    """ Just allows wrapping the entire ScFeatured as a GtkRevealer
        Will also handle the initial transition view for showing the
        revealer contents once loading has completed """

    widget = None
    loaded = None

    def __init__(self, context):
        Gtk.Revealer.__init__(self)
        self.context = context
        self.loaded = False
        self.context.connect('loaded', self.on_context_loaded)
        self.widget = ScFeatured(context)

        self.add(self.widget)
        self.set_reveal_child(False)
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)

    def on_context_loaded(self, context):
        """ Fill the featured view in  """
        for plugin in self.context.plugins:
            # Build the featured view
            plugin.populate_storage(
                self.widget, PopulationFilter.FEATURED,
                self.context.appsystem)
        self.loaded = True
        self.slide_down_show()

    def slide_up_hide(self):
        """ Slide up out of view """
        if not self.get_visible() or not self.get_child_visible():
            return
        if not self.loaded:
            return
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        self.set_reveal_child(False)

    def slide_down_show(self):
        """ Slide into view """
        if not self.get_visible() or not self.get_child_visible():
            return
        if not self.loaded:
            return
        self.set_transition_type(Gtk.RevealerTransitionType.SLIDE_UP)
        self.set_reveal_child(True)
