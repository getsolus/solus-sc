#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import AppStreamGlib as As
from gi.repository import Gio, GLib, GdkPixbuf, Gtk, Gdk


class Screenshot:
    """ Wrap AppStream screenshots into something usable. """

    main_uri = None
    thumb_uri = None
    default = None

    def __init__(self, asImg, scale):
        large = None
        normal = None
        thumbnail = None

        if asImg.get_kind() == As.ScreenshotKind.DEFAULT:
            self.default = True
        else:
            self.default = False

        # Loop em all with scale factor
        for image in asImg.get_images():
            if image.get_width() == As.IMAGE_LARGE_WIDTH * scale:
                large = image
            elif image.get_width() == As.IMAGE_NORMAL_WIDTH * scale:
                normal = image
            elif image.get_width() == As.IMAGE_THUMBNAIL_WIDTH * scale:
                thumbnail = image
            if large and normal and thumbnail:
                break
        # Couldn't find with scale factor so try with normal sizes
        if scale != 1:
            if not thumbnail or not normal:
                for image in asImg.get_images():
                    if image.get_width() == As.IMAGE_LARGE_WIDTH:
                        large = image
                    elif image.get_width() == As.IMAGE_NORMAL_WIDTH:
                        normal = image
                    elif image.get_width() == As.IMAGE_THUMBNAIL_WIDTH:
                        thumbnail = image
                    if large and normal and thumbnail:
                        break

        if large is None:
            large = normal

        if not normal or not thumbnail:
            raise RuntimeError("Invalid screenshot")

        self.main_uri = large.get_url()
        self.thumb_uri = thumbnail.get_url()


class AppSystem:
    """ Mux calls into AppStream where appropriate.

        This class enables failsafe queries for descriptions/summaries
        by hooking into AppSystem, and falling back to the native fields
        in the .eopkg's

        TODO: Locale integration
    """

    store = None

    store = None
    fetcher = None

    scale_factor = 1
    window = None

    def __init__(self):
        self.store = As.Store()
        self.store.load(As.StoreLoadFlags.APP_INFO_SYSTEM)

    def sanitize(self, text):
        return text.replace("&quot;", "\"")

    def get_store_variant(self, store, id):
        """ Helper to find the package """
        if not store:
            store = self.store
        ret = store.get_app_by_pkgname(id)
        if ret:
            return ret
        ret = store.get_app_by_id(id)
        if ret:
            return ret
        return store.get_app_by_id(id + ".desktop")

    def get_summary(self, id, fallback, store=None):
        """ Return a usable summary for a package """
        app = self.get_store_variant(store, id)
        ret = None
        if not app:
            ret = GLib.markup_escape_text(str(fallback))
        else:
            ret = app.get_comment("C")
        if not ret:
            return self.sanitize(fallback)
        return self.sanitize(ret)

    def get_description(self, id, fallback, store=None):
        """ Return a usable description for a package """
        app = self.get_store_variant(store, id)
        if not app:
            return self.sanitize(
                GLib.markup_escape_text(str(fallback)))
        c = app.get_description("C")
        if not c:
            return self.sanitize(
                GLib.markup_escape_text(str(fallback)))
        return c

    def get_name(self, id, fallback, store=None):
        app = self.get_store_variant(store, id)
        if not app:
            return GLib.markup_escape_text(str(fallback))
        ret = app.get_name("C")
        if not ret:
            return self.sanitize(fallback)
        return GLib.markup_escape_text(self.sanitize(ret))

    def _get_appstream_url(self, id, ptype, store):
        """ Get an appstream link for the given package """
        app = self.get_store_variant(store, id)
        if not app:
            return None
        url = app.get_url_item(ptype)
        return url

    def get_website(self, id, fallback, store=None):
        """ Get the website for a given package """
        home = self._get_appstream_url(id, As.UrlKind.HOMEPAGE, store)
        if home:
            return home
        if fallback:
            return str(fallback)
        return None

    def find_icon(self, app, width, height):
        """ AppStream will happily give us remote icons when we'll only look
            to load locally sourced ones in the icon cache. It will also give
            us remote ones before a locally existing one so we have to do
            the iteration ourselves.
        """
        for icon in app.get_icons():
            kind = icon.get_kind()
            if kind == As.IconKind.UNKNOWN or kind == As.IconKind.REMOTE:
                continue
            iwidth = icon.get_width() / icon.get_scale()
            iheight = icon.get_height() / icon.get_scale()
            if iwidth == width and iheight == height:
                return icon
        return app.get_icon_for_size(width, height)

    def set_fallback_icon(self, image):
        image.set_from_icon_name("package-x-generic", Gtk.IconSize.INVALID)

    def set_image_from_item(self, image, item, store=None, size=64):
        """ Set the GtkImage if possible """
        icon_name = item.get_icon_name()
        if icon_name:
            image.set_from_icon_name(icon_name, Gtk.IconSize.INVALID)
            return

        # Grab app bits
        id = item.get_id()
        app = self.get_store_variant(store, id)

        # No app? Set default icon for hidpi support.
        if not app:
            self.set_fallback_icon(image)
            return

        original_size = size
        size = size * self.scale_factor

        # No icon?
        icon = self.find_icon(app, size, size)
        if not icon:
            size /= self.scale_factor
            icon = self.find_icon(app, size, size)
        if not icon:
            self.set_fallback_icon(image)
            return

        # Find out what kind of icon this is
        kind = icon.get_kind()
        if kind == As.IconKind.STOCK:
            image.set_from_icon_name(icon.get_name(), Gtk.IconSize.INVALID)
            return

        # We're dealing with an unknown
        if kind == As.IconKind.UNKNOWN or kind == As.IconKind.REMOTE:
            self.set_fallback_icon(image)
            return

        icon.set_scale(self.scale_factor)
        # Try to load the cached/available icon
        try:
            if not icon.load(As.IconLoadFlags.SEARCH_SIZE):
                self.set_fallback_icon(image)
                return
        except Exception as e:
            print("Should not happen: {}".format(e))
            self.set_fallback_icon(image)
            return

        # At this point we're dealing with pixbufs
        pbuf = icon.get_pixbuf()

        # Ew.
        if pbuf.get_height() != original_size * self.scale_factor:
            pbuf = pbuf.scale_simple(
                original_size * self.scale_factor,
                original_size * self.scale_factor,
                GdkPixbuf.InterpType.BILINEAR)

        if self.scale_factor == 1:
            image.set_from_pixbuf(pbuf)
            return

        window = self.window.get_window()
        if not window:
            self.set_fallback_icon(image)
            return

        try:
            surface = Gdk.cairo_surface_create_from_pixbuf(
                pbuf,
                self.scale_factor,
                window)
            image.set_from_surface(surface)
        except Exception as e:
            print(e)
            self.set_fallback_icon(image)

    def get_donation_site(self, id, store=None):
        """ Get a donation link for the given package """
        return self._get_appstream_url(id, As.UrlKind.DONATION, store)

    def get_bug_site(self, id, store=None):
        """ Get a bug link for the given package """
        return self._get_appstream_url(id, As.UrlKind.BUGTRACKER, store)

    def get_developers(self, id, store=None):
        """ Get the developer names for the given package """
        app = self.get_store_variant(store, id)
        if not app:
            return None
        return app.get_developer_name("C")

    def get_screenshots(self, id, store=None):
        """ Return wrapped Screenshot objects for the package """
        app = self.get_store_variant(store, id)
        if not app:
            return None
        screens = app.get_screenshots()
        if not screens:
            return None
        ret = []
        for screen in screens:
            try:
                img = Screenshot(screen, self.scale_factor)
                ret.append(img)
            except Exception as e:
                print("Unable to load screen: {}".format(e))
        return ret

    def get_launchable_id(self, id, store=None):
        """ Return the desktop file id for the given package """
        app = self.get_store_variant(store, id)
        if not app:
            return None
        launch = app.get_launchable_by_kind(As.LaunchableKind.DESKTOP_ID)
        if launch is None:
            return None

        return launch.get_value()
