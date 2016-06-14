#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import AppStreamGlib as As
from gi.repository import Gio, GLib, Gtk


class AppSystem:
    """ Mux calls into AppStream where appropriate.

        This class enables failsafe queries for descriptions/summaries
        by hooking into AppSystem, and falling back to the native fields
        in the .eopkg's

        TODO: Locale integration
    """

    store = None
    default_pixbuf = None

    def __init__(self):
        self.store = As.Store()
        self.store.load(As.StoreLoadFlags.APP_INFO_SYSTEM)

        itheme = Gtk.IconTheme.get_default()
        try:
            self.default_pixbuf = itheme.load_icon(
                "package-x-generic",
                64,
                Gtk.IconLookupFlags.GENERIC_FALLBACK)
        except Exception as e:
            print(e)

    def sanitize(self, text):
        return text.replace("&quot;", "\"")

    def get_summary(self, package):
        """ Return a usable summary for a package """
        app = self.store.get_app_by_pkgname(package.name)
        ret = None
        if not app:
            ret = GLib.markup_escape_text(str(package.summary))
        else:
            ret = app.get_comment("C")
        return self.sanitize(ret)

    def get_description(self, package):
        """ Return a usable description for a package """
        app = self.store.get_app_by_pkgname(package.name)
        if not app:
            return self.sanitize(
                GLib.markup_escape_text(str(package.description)))
        c = app.get_description("C")
        if not c:
            return self.sanitize(
                GLib.markup_escape_text(str(package.description)))
        return c

    def get_name(self, package):
        app = self.store.get_app_by_pkgname(package.name)
        if not app:
            return package.name
        return self.sanitize(app.get_name("C"))

    def get_icon(self, package):
        """ Fallback method """
        if package.icon:
            return package.icon
        return "package-x-generic"

    def get_pixbuf(self, package):
        """ Get the AppStream GdkPixbuf for a package """
        app = self.store.get_app_by_pkgname(package.name)
        if not app:
            return None
        # TODO: Incorporate HIDPI!
        icon = app.get_icon_for_size(64, 64)
        if not icon:
            return None
        kind = icon.get_kind()
        if kind == As.IconKind.UNKNOWN or kind == As.IconKind.REMOTE:
            return None
        if kind == As.IconKind.STOCK:
            # Load up a gthemedicon version
            im = Gio.ThemedIcon.new(icon.get_name())
            return im
        if not icon.load(As.IconLoadFlags.SEARCH_SIZE):
            return None
        return icon.get_pixbuf()

    def get_pixbuf_only(self, package):
        """ Only get a pixbuf - no fallbacks  """
        app = self.store.get_app_by_pkgname(package.name)
        if not app:
            return self.default_pixbuf
        # TODO: Incorporate HIDPI!
        icon = app.get_icon_for_size(64, 64)
        if not icon:
            return self.default_pixbuf
        kind = icon.get_kind()
        if kind == As.IconKind.UNKNOWN or kind == As.IconKind.REMOTE:
            return None
        if kind == As.IconKind.STOCK:
            # Load up a gthemedicon version
            try:
                itheme = Gtk.IconTheme.get_default()
                pbuf = itheme.load_icon(
                    icon.get_name(),
                    64,
                    Gtk.IconLookupFlags.GENERIC_FALLBACK)
                return pbuf
            except Exception as e:
                print(e)
            return self.default_pixbuf
        if not icon.load(As.IconLoadFlags.SEARCH_SIZE):
            return self.default_pixbuf
        return icon.get_pixbuf()

    def get_website(self, package):
        """ Get the website for a given package """
        app = self.store.get_app_by_pkgname(package.name)
        if not app:
            if package.source.homepage:
                return str(package.source.homepage)
            return None
        url = app.get_url_item(As.UrlKind.HOMEPAGE)
        return url

    def get_donation_site(self, package):
        """ Get a donation link for the given package """
        app = self.store.get_app_by_pkgname(package.name)
        if not app:
            return None
        url = app.get_url_item(As.UrlKind.DONATION)
        return url
