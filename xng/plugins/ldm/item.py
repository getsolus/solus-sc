#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from ..base import ProviderItem, ItemStatus

from gi.repository import Ldm, Gtk, GdkPixbuf


class LdmItem(ProviderItem):
    """ Toplevel plugin category to allow browsing """

    __gtype_name__ = "NxLdmItem"

    device = None
    icon_name = None

    def __init__(self, device):
        ProviderItem.__init__(self)
        self.device = device
        self.add_status(ItemStatus.META_HARDWARE)

        if self.device.has_type(Ldm.DeviceType.GPU):
            self.icon_name = "preferences-desktop-display"
        elif self.device.has_type(Ldm.DeviceType.HID):
            if "keyboard" in self.device.get_name().lower():
                self.icon_name = "keyboard"
            else:
                self.icon_name = "preferences-desktop-mouse"
        elif self.device.has_type(Ldm.DeviceType.PRINTER):
            self.icon_name = "printer"

    def get_id(self):
        return "ldm:" + str(self.device.get_path())

    def format_full_name(self):
        return "{} {}".format(
            self.device.get_vendor(),
            self.device.get_name())

    def get_name(self):
        return self.format_full_name()

    def get_summary(self):
        return self.device.get_name()

    def get_title(self):
        return self.format_full_name()

    def get_description(self):
        return self.device.get_name()

    def get_version(self):
        return ""

    def get_icon_name(self):
        return self.icon_name
