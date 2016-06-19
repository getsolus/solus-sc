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

import dbus


class PolkitHelper:
    """ PolKit helper, reused in a billion projects by now, stolen from our
        own solusconfig from back in the day. """

    def check_authorization(self, pid, action_id):
        # PolicyKit lives on the system bus
        bus = dbus.SystemBus()
        proxy = bus.get_object('org.freedesktop.PolicyKit1',
                               '/org/freedesktop/PolicyKit1/Authority')

        pk_authority = dbus.Interface(
            proxy,
            dbus_interface='org.freedesktop.PolicyKit1.Authority')

        # We're enquiring about this process
        subject = ('unix-process',
                   {
                       'pid': dbus.UInt32(pid, variant_level=1),
                       'start-time': dbus.UInt64(0, variant_level=1)
                   })

        # No cancellation.
        cancel_id = ''

        # AllowUserInteractionFlag
        flags = dbus.UInt32(1)

        # Only for trusted senders, rarely used.
        details = {}

        (pk_granted, pk_other, pk_details) = pk_authority.CheckAuthorization(
            subject, action_id, details, flags, cancel_id, timeout=600)

        return pk_granted
