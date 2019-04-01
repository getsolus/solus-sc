#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2019 Solus
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import GObject
import os


class ScDesktopClass:
    """ Crappy enum to represent desktop class """

    GNOME = 1
    KDE = 2
    MATE = 3
    BUDGIE = 4
    UNKNOWN = 5


class ScDesktopIntegration(GObject.Object):
    """ The DesktopIntegration class provides some helpers to facilitate
        with better integrating the Software Center with the current
        desktop.

        It can be accessed via the context.desktop variable.
    """

    __gtype_name__ = "ScDesktopIntegration"

    desktop_classes = None

    def __init__(self):
        GObject.Object.__init__(self)
        self.desktop_classes = set()

        self.init_desktop_classes()

    def init_desktop_classes(self):
        """ Accumulate the desktop classes to figure out what we're dealing
            with so we know the capabilities ahead of time """
        desktops = None
        if "XDG_CURRENT_DESKTOP" in os.environ:
            desktop = os.environ["XDG_CURRENT_DESKTOP"]
            desktops = desktop.strip().lower().split(":")

        # Try to figure out without XDG_CURRENT_DESKTOP
        if not desktops:
            if "GNOME_DESKTOP_SESSION_ID" in os.environ:
                self.desktop_classes = [ScDesktopClass.GNOME]
            else:
                self.desktop_classes = [ScDesktopClass.UNKNOWN]
            return

        # Deal with the XDG_CURRENT_DESKTOP set
        for identifier in desktops:
            identifier = identifier.lower().strip()

            if identifier == "gnome":
                self.desktop_classes.add(ScDesktopClass.GNOME)
            elif identifier == "budgie":
                self.desktop_classes.add(ScDesktopClass.BUDGIE)
            elif identifier == "mate":
                self.desktop_classes.add(ScDesktopClass.MATE)
            elif identifier == "kde":
                self.desktop_classes.add(ScDesktopClass.KDE)

        if len(self.desktop_classes) < 1:
            self.desktop_classes.add(ScDesktopClass.UNKNOWN)

    def has_desktop_class(self, dclass):
        """ Return True if the running desktop has the given class """
        return dclass in self.desktop_classes

    def should_csd(self):
        """ Return True if we should use CSD with the current desktop """
        return not self.has_desktop_class(ScDesktopClass.KDE)
