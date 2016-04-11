#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright 2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#

from pisi.db.packagedb import PackageDB
from pisi.db.installdb import InstallDB
import pisi.specfile
import re

cve_hit = re.compile(r".*(CVE\-[0-9]+\-[0-9]+).*")


def cves_for_update(update):
    ''' Grab a list of CVEs addressed in this version '''
    cves = set()

    com = str(update.comment)
    for i in com.split(" "):
        m = cve_hit.match(i)
        if not m:
            continue
        cves.add(m.group(1))

    return cves


def get_history_between(old, new):
    ret = list()

    for i in new.history:
        if i.release <= old.release:
            continue
        ret.append(i)
    return ret


def get_cve_uri(i):
    return "http://cve.mitre.org/cgi-bin/cvename.cgi?name={}".format(i)


def get_pkg_description(pkg):
    return "{}-{}-{}".format(pkg.name, pkg.version, pkg.release)


def main():
    pkg = "glibc"

    pdb = PackageDB()
    package = pdb.get_package(pkg)
    idb = InstallDB()

    local_package = idb.get_package(pkg)
    # HACK for testing!!
    local_package.release = 18
    local_package.version = "2.22"

    new_package = pdb.get_package(pkg)

    history = get_history_between(local_package, new_package)

    cves = list()
    for x in history:
        c = cves_for_update(x)
        if not c:
            continue
        cves.extend(c)

    o = get_pkg_description(local_package)
    n = get_pkg_description(new_package)

    print("CVEs fixed between {} and {}: {}".format(o, n, ", ".join(cves)))


if __name__ == "__main__":
    main()
