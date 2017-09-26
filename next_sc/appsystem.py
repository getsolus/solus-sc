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

from gi.repository import AppStreamGlib as As
from gi.repository import Gio, GLib, GdkPixbuf, Gtk


class AppSystem:
    """ Mux calls into AppStream where appropriate.

        This class enables failsafe queries for descriptions/summaries
        by hooking into AppSystem, and falling back to the native fields
        in the .eopkg's

        TODO: Locale integration
    """

    store = None

    def __init__(self):
        self.store = As.Store()
        self.store.load(As.StoreLoadFlags.APP_INFO_SYSTEM)

    def sanitize(self, text):
        return text.replace("&quot;", "\"")

    def get_summary(self, id, fallback):
        """ Return a usable summary for a package """
        app = self.store.get_app_by_pkgname(id)
        ret = None
        if not app:
            ret = GLib.markup_escape_text(str(fallback))
        else:
            ret = app.get_comment("C")
        return self.sanitize(ret)

    def get_description(self, id, fallback):
        """ Return a usable description for a package """
        app = self.store.get_app_by_pkgname(id)
        if not app:
            return self.sanitize(
                GLib.markup_escape_text(str(fallback)))
        c = app.get_description("C")
        if not c:
            return self.sanitize(
                GLib.markup_escape_text(str(fallback)))
        return c

    def get_name(self, id, fallback):
        app = self.store.get_app_by_pkgname(id)
        if not app:
            return GLib.markup_escape_text(str(fallback))
        return GLib.markup_escape_text(self.sanitize(app.get_name("C")))

    def _get_appstream_url(self, id, ptype):
        """ Get an appstream link for the given package """
        app = self.store.get_app_by_pkgname(id)
        if not app:
            return None
        url = app.get_url_item(ptype)
        return url

    def get_website(self, id, fallback):
        """ Get the website for a given package """
        home = self._get_appstream_url(id, As.UrlKind.HOMEPAGE)
        if home:
            return home
        if fallback:
            return str(fallback)
        return None

    def get_donation_site(self, id):
        """ Get a donation link for the given package """
        return self._get_appstream_url(id, As.UrlKind.DONATION)

    def get_bug_site(self, id):
        """ Get a bug link for the given package """
        return self._get_appstream_url(id, As.UrlKind.BUGTRACKER)

    def get_developers(self, id):
        """ Get the developer names for the given package """
        app = self.store.get_app_by_pkgname(id)
        if not app:
            return None
        return app.get_developer_name("C")
