#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2017-2020 Solus
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk
from random import randint


class ScLoadingPage(Gtk.VBox):
    """ Simple loading page, nothing fancy. """

    spinner = None
    messages = None

    def __init__(self, message=None):
        Gtk.VBox.__init__(self)

        # Random messages
        self.messages = [
            _("Switching to the B-side of the cassette"),
            _("Solving the Paradox Of Choice"),
            _("Blasting regex across repo index"),
            _("Seat-dancing intensifies"),
        ]

        self.set_valign(Gtk.Align.CENTER)
        self.set_halign(Gtk.Align.CENTER)
        self.spinner = Gtk.Spinner()
        self.spinner.set_size_request(-1, 64)
        self.spinner.start()
        # Loading available packages (witty loading screen)
        self.label = Gtk.Label()
        self.set_message(message)

        self.pack_start(self.spinner, True, True, 0)
        self.pack_start(self.label, False, False, 0)
        self.label.set_property("margin", 20)

        # Ensure some kind of message is set initially
        self.set_message(message)

    def set_message(self, message=None):
        if not message:
            message = self.random_message()
        message = message.decode('utf-8')
        self.label.set_markup(u"<big>{}…</big>".format(message))

    def random_message(self):
        i = randint(0, len(self.messages) - 1)
        return self.messages[i]

    def start(self):
        """ Start the idle spinner """
        self.spinner.start()

    def stop(self):
        """ Stop the idle spinner """
        self.spinner.stop()

    def get_page_name(self):
        """ Allow using this as a primary page """
        return _("Loading")
