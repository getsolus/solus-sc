#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gio

SC_UPDATE_APP_ID = "com.solus_project.UpdateChecker"


class ScUpdateApp(Gio.Application):

    def __init__(self):
        Gio.Application.__init__(self,
                                 application_id=SC_UPDATE_APP_ID,
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)

    def on_activate(self, app):
        self.begin_background_checks()

    def begin_background_checks(self):
        pass
