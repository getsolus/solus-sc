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

class LdmRootCategory(ProviderCategory):

    __gtype_name__ = "NxLdmRootCategory"

    def __init__(self):
        ProviderCategory.__init__(self)

    def get_icon_name(self):
        return "cs-cat-hardware"

    def get_id(self):
        return "ldm-category"

    def get_name(self):
        return _("Hardware & Drivers")
