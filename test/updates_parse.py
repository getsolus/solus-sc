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


def main():
    pkg = "glibc"

    pdb = PackageDB()
    package = pdb.get_package(pkg)

    cves = set()

    for item in package.history:
        com = str(item.comment)
        for i in com.split(" "):
            m = cve_hit.match(i)
            if not m:
                continue
            cves.add(m.group(1))

    c = ", ".join(cves)
    print("CVE history for {}: {}".format(pkg, c))
    pass


if __name__ == "__main__":
    main()
