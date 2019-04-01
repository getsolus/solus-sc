#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2019 Solus
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

import gi
gi.require_version('Ldm', '1.0')
from gi.repository import Ldm
import pisi.db
import os


class Kernel:
    """ Kernel object to map real kernels to package manager """

    ipkg = None
    running = None
    variant = None
    fpath = None
    name = None

    def __init__(self, ipkg, variant, fpath):
        """ Create a new kernel object from the given ipkg """
        self.ipkg = ipkg
        self.name = self.ipkg.name
        self.running = False
        self.variant = variant
        self.fpath = fpath


def accumulate_official_kernels(idb):
    """ Search the users system for installed kernels that are from us. """
    avail_kernels = set()
    uname = os.uname()
    kernel = uname[2]
    variant = kernel.split(".")[-1]
    start = kernel[0:len(kernel)-len(variant)-1]
    ttype = "{}.{}".format(variant, start)

    # Learn kernels
    for i in os.listdir("/usr/lib/kernel"):
        fpath = os.path.join("/usr/lib/kernel", i)
        if not i.startswith("default-"):
            continue
        if not os.path.islink(fpath):
            continue
        link = None
        try:
            link = os.path.realpath(fpath)
        except:
            continue

        # Only interested in properly installed kernels
        link_base = os.path.basename(link)
        cur_variant = i.split("default-")[1]
        pkgname = "linux-{}".format(cur_variant)
        if not idb.has_package(pkgname):
            continue

        ipkg = idb.get_package(pkgname)
        kernel = Kernel(ipkg, cur_variant, link_base)
        if kernel.fpath.endswith(ttype):
            kernel.running = True
        avail_kernels.add(kernel)

    return avail_kernels


def get_provider_packages(kernels, pkgdb, pkgname):
    """ Covert the package name in LDM to something we care about """
    search = [pkgname]
    search.extend("{}-{}".format(pkgname, k.variant) for k in kernels)
    ret = []
    for s in search:
        if not pkgdb.has_package(s):
            continue
        pkg = pkgdb.get_package(s)
        ret.append(pkg)
    return ret


def test_device(kernels, pkgdb, manager, device):
    providers = manager.get_providers(device)
    if not providers:
        return

    print("Providers for {} {} ({})".format(
        device.props.vendor, device.props.name, device.props.path))
    for provider in providers:
        for pkg in get_provider_packages(kernels, pkgdb, provider.get_package()):
            print(pkg.name)


def main():
    """ Test LDM Hardware stuffs. """
    manager = Ldm.Manager.new(Ldm.ManagerFlags.NO_MONITOR)
    manager.add_system_modalias_plugins()

    pkgdb = pisi.db.packagedb.PackageDB()
    idb = pisi.db.installdb.InstallDB()
    kernels = accumulate_official_kernels(idb)

    gpu_config = Ldm.GPUConfig.new(manager)
    devices = [x for x in manager.get_devices(
        0) if not x.has_type(Ldm.DeviceType.GPU)]
    devices.append(gpu_config.get_detection_device())
    for device in devices:
        test_device(kernels, pkgdb, manager, device)


if __name__ == "__main__":
    main()
