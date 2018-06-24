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

from ..base import ProviderCategory

from gi.repository import Ldm


class LdmRootCategory(ProviderCategory):
    """ Toplevel plugin category to allow browsing """

    __gtype_name__ = "NxLdmRootCategory"

    children = None

    def __init__(self):
        ProviderCategory.__init__(self)

        self.children = [
            LdmCategory(Ldm.DeviceType.ANY),
            LdmCategory(Ldm.DeviceType.GPU),
            LdmCategory(Ldm.DeviceType.HID),
            LdmCategory(Ldm.DeviceType.PRINTER),
        ]

    def get_children(self):
        return self.children

    def get_icon_name(self):
        return "cs-cat-hardware"

    def get_id(self):
        return "ldm:root"

    def get_name(self):
        return _("Hardware & Drivers")


class LdmCategory(ProviderCategory):
    """ Child-level category to allow browsing hardware """

    __gtype_name__ = "NxLdmCategory"

    display_icon = None  # The icon our category holds
    display_name = None  # The name our category holds
    ldm_type = None  # Filtered device types
    cat_name = None

    def __init__(self, ldm_type):
        self.ldm_type = ldm_type

        self.mappings = {
            Ldm.DeviceType.ANY: (
                _("All"), "ldm:all", "starred"
            ),
            Ldm.DeviceType.GPU: (
                _("GPU Devices"), "ldm:gpu", "preferences-desktop-display"
            ),
            Ldm.DeviceType.HID: (
                _("HID Devices"), "ldm:hid", "preferences-desktop-mouse"
            ),
            Ldm.DeviceType.PRINTER: (
                _("Printers"), "ldm:printer", "printer"
            ),
        }
        self.assign_attributes()

    def assign_attributes(self):
        """ Add our attributes based on our primary device type """
        if self.ldm_type in self.mappings:
            tupleset = self.mappings[self.ldm_type]
            self.display_name = tupleset[0]
            self.cat_name = tupleset[1]
            self.display_icon = tupleset[2]
        else:
            self.cat_name = "ldm:broken"
            self.display_icon = "image-missing"
            self.display_name = "!!broken!!"

    def get_icon_name(self):
        return self.display_icon

    def get_id(self):
        return self.cat_name

    def get_name(self):
        return self.display_name
