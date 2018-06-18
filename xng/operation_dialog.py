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


class ScOperationDialog(Gtk.Dialog):
    """ Shows details about an install/remove operation before doing it.

        The details view is effectively the pretty view with all the relevant
        package/software details, screenshots, and actions to invoke removal,
        installation, etc.
    """

    __gtype_name__ = "ScOperationDialog"

    def __init__(self, window):
        Gtk.Dialog.__init__(self, transient_for=window, use_header_bar=1)
        self.set_title("Add witty title here")

    def prepare(self, item, operation_type):
        self.show_all()
        print(operation_type, item)
