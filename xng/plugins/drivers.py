#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2018 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#


from gi.repository import GObject, Ldm


class DriverProvider(GObject.Object):
    """ Simple wrapper around package (base) name and a Provider object

        We need this as a reverse lookup for a set of names, basically.
    """

    name = None
    priority = None
    device = None

    def __init__(self, provider):
        self.name = provider.get_package()
        self.priority = provider.get_plugin().get_priority()
        self.device = provider.get_device()


class DriverManager(GObject.Object):
    """ Simple wrapper around Ldm

        We need this wrapper to make sure the Software Center can survive
        updates that alter LDM, such as the gi.require_version() call perhaps
        changing in future. So that the Software Center doesn't crash, we
        dynamically import at startup and just continue regardless.
    """

    __gtype_name__ = "DriverManager"
    manager = None

    mapping = None

    def __init__(self):
        self.manager = Ldm.Manager.new(Ldm.ManagerFlags.NO_MONITOR)

    def reload(self):
        """ Reload the DriverManager and rediscover all providers """
        self.manager.add_system_modalias_plugins()
        self.mapping = dict()  # Purge old entries

        # Locate all providers at this point
        devices = self.manager.get_devices(0)

        # We don't want to detect drivers for ALL GPUs, just the detection one
        checks = [x for x in devices if not x.has_type(Ldm.DeviceType.GPU)]

        # Grab the primary GPU detection device
        try:
            gpu = Ldm.GPUConfig.new(self.manager)
            gpu_device = gpu.get_detection_device()
            if gpu_device:
                checks.append(gpu_device)
        except Exception as ex:
            print("Cannot detect system GPU: {}".format(ex))

        for device in checks:
            for provider in self.manager.get_providers(device):
                self.push_provider(provider)

    def push_provider(self, provider):
        """ Push an LdmProvider into our storage """
        prov = DriverProvider(provider)
        if prov.name not in self.mapping:
            self.mapping[prov.name] = list()
        self.mapping[prov.name].append(prov)

    def get_providers_for_name(self, name):
        """ Return providers for the given package name """
        if name not in self.mapping:
            return None
        return self.mapping[name]
