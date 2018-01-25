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
from .imagewidget import ScImageWidget


class ScScreenshotView(Gtk.Box):
    """ Holds all the internal details of a screenshots view, and is owned
        typically be the details page """

    fetcher = None
    screen_map = None

    image_widget = None
    box_thumbnails = None

    def __init__(self, context):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL)
        self.context = context
        self.context.connect('loaded', self.on_context_loaded)

        # Set up our alignment
        self.set_valign(Gtk.Align.START)
        self.set_halign(Gtk.Align.START)

        # Main screenshot
        self.image_widget = ScImageWidget()
        self.image_widget.set_margin_bottom(10)
        self.image_widget.set_margin_top(30)
        self.image_widget.show_all()
        self.image_widget.set_no_show_all(True)
        self.image_widget.hide()
        self.pack_start(self.image_widget, False, False, 0)

        # And the thumbnails in horizontal-only scroller
        self.box_thumbnails = Gtk.FlowBox()
        self.box_thumbnails.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.box_thumbnails.connect("selected-children-changed",
                                    self.on_thumbnail_selected)
        self.box_thumbnails.set_activate_on_single_click(True)
        # The rest forces a single line horizontal row. Not kidding.
        self.box_thumbnails.set_homogeneous(False)
        self.box_thumbnails.set_valign(Gtk.Align.START)
        self.box_thumbnails.set_halign(Gtk.Align.CENTER)
        self.box_thumbnails.set_vexpand(False)
        self.box_thumbnails.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.box_thumbnails.set_max_children_per_line(4)
        thumb_wrap = Gtk.ScrolledWindow(None, None)
        thumb_wrap.set_halign(Gtk.Align.START)
        # thumb_wrap.set_overlay_scrolling(False)
        thumb_wrap.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        thumb_wrap.add(self.box_thumbnails)
        thumb_wrap.set_margin_bottom(10)
        thumb_wrap.set_margin_start(10)
        thumb_wrap.set_margin_top(30)
        self.pack_start(thumb_wrap, False, False, 0)

    def on_context_loaded(self, context):
        """ Bind to the fetcher now it's available """
        self.fetcher = context.fetcher
        self.screen_map = dict()
        self.fetcher.connect('media-fetched', self.on_media_fetched)
        self.fetcher.connect('fetch-failed', self.on_fetch_failed)

    def on_media_fetched(self, fetcher, uri, filename, pixbuf):
        """ Some media that we asked for has been loaded """
        # Check if its our main preview
        if uri == self.image_widget.uri:
            self.image_widget.show_image(uri, pixbuf)
            self.image_widget.queue_resize()
        elif uri in self.screen_map:
            wid = self.screen_map[uri]
            wid.show_image(uri, pixbuf)
            wid.queue_resize()
        pixbuf = None

    def on_fetch_failed(self, fetcher, uri, err):
        """ We failed to fetch *something* """
        if uri == self.image_widget.uri:
            self.image_widget.show_failed(uri, err)
            self.image_widget.queue_resize()
        elif uri in self.screen_map:
            wid = self.screen_map[uri]
            wid.show_failed(uri, err)
            wid.queue_resize()

    def on_thumbnail_selected(self, fbox):
        """ Thumbnail selected, request view of Big Picture """
        selection = fbox.get_selected_children()
        if not selection or len(selection) < 1:
            return
        child = selection[0]
        thumb = child.get_child()
        # Nothing to be done here
        if self.image_widget.uri == thumb.alt_uri:
            return
        # Request show of new picture
        self.image_widget.show_loading()
        self.image_widget.uri = thumb.alt_uri
        self.fetcher.fetch_media(thumb.alt_uri)

    def set_item(self, item):
        # Clean up old thumbnails
        for child in self.box_thumbnails.get_children():
            child.destroy()
            child = None
        keys = self.screen_map.keys()
        for key in keys:
            del self.screen_map[key]
        self.screen_map = dict()

        # Ask AppSystem for screenshots (AppStream only!)
        id = item.get_id()
        apps = self.context.appsystem
        screens = apps.get_screenshots(id)
        if not screens:
            self.image_widget.hide()
            self.image_widget.show_not_found()
            return
        self.image_widget.show()
        # Update the UI immediately to show we're going to load
        self.image_widget.show_loading()
        default = None
        for scr in screens:
            if scr.default:
                default = scr
        if not default:
            default = screens[0]
        self.image_widget.uri = default.main_uri
        # Always "fetch", fetcher knows if it exists or not.
        self.fetcher.fetch_media(default.main_uri)

        # Set up the screenshot order
        allScreens = [default]
        allScreens.extend([x for x in screens if x != default])

        # No point showing thumbnails when only one screenshot is available
        if len(allScreens) < 2:
            return
        defaultParent = None

        # Set up all the screenshot thumbnails
        for screen in allScreens:
            preview = ScImageWidget(thumbnail=True)
            self.box_thumbnails.add(preview)
            preview.show_all()
            preview.alt_uri = screen.main_uri
            preview.uri = screen.thumb_uri
            preview.show_loading()
            if screen == default:
                defaultParent = preview.get_parent()
            preview.get_parent().set_margin_bottom(8)
            self.screen_map[screen.thumb_uri] = preview

        # Now ask the preview to fetch
        for screen in allScreens:
            self.fetcher.fetch_media(screen.thumb_uri)

        # And now select it
        self.box_thumbnails.select_child(defaultParent)
