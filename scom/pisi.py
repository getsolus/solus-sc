#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2009 TUBITAK/UEKAE
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# Please read the COPYING file.
#

# Disable cyclic garbage collector of Python to avoid comar segmentation
# faults under high load (#11110)
import gc
gc.disable()

import os
import os.path
import locale
import string
import functools

# FIXME: later this will be Comar's job
systemlocale = open("/etc/mudur/locale", "r").readline().strip()

# for pisi
os.environ["LC_ALL"] = systemlocale

# for system error messages
locale.setlocale(locale.LC_ALL, systemlocale)

try:
    import pisi.api
    import pisi.db
    import pisi.ui
    import pisi.util as util
    import pisi.configfile
    from pisi.version import Version
except KeyboardInterrupt:
    notify("System.Manager", "cancelled", "")

class UI(pisi.ui.UI):
    def error(self, msg):
        notify("System.Manager", "error", str(msg))

    def warning(self, msg):
        notify("System.Manager", "warning", str(msg))

    def notify(self, event, **keywords):
        if event == pisi.ui.installing:
            pkgname = keywords["package"].name
            notify("System.Manager", "status", ("installing", pkgname, "", ""))
        elif event == pisi.ui.configuring:
            pkgname = keywords["package"].name
            notify("System.Manager", "status", ("configuring", pkgname, "", ""))
        elif event == pisi.ui.extracting:
            pkgname = keywords["package"].name
            notify("System.Manager", "status", ("extracting", pkgname, "", ""))
        elif event == pisi.ui.updatingrepo:
            reponame = keywords["name"]
            notify("System.Manager", "status", ("updatingrepo", reponame, "", ""))
        elif event == pisi.ui.removing:
            pkgname = keywords["package"].name
            notify("System.Manager", "status", ("removing", pkgname, "", ""))
        elif event == pisi.ui.cached:
            total = str(keywords["total"])
            cached = str(keywords["cached"])
            notify("System.Manager", "status", ("cached", total, cached, ""))
        elif event == pisi.ui.installed:
            notify("System.Manager", "status", ("installed", "", "", ""))
        elif event == pisi.ui.removed:
            notify("System.Manager", "status", ("removed", "", "", ""))
        elif event == pisi.ui.upgraded:
            notify("System.Manager", "status", ("upgraded", "", "", ""))
        elif event == pisi.ui.packagestogo:
            notify("System.Manager", "status", ("order", "", "", ""))
        elif event == pisi.ui.desktopfile:
            filepath = keywords["desktopfile"]
            notify("System.Manager", "status", ("desktopfile", filepath, "", ""))
        elif event == pisi.ui.systemconf:
            notify("System.Manager", "status", ("systemconf", "", "", ""))
        else:
            return

    def ack(self, msg):
        return True

    def confirm(self, msg):
        return True

    def display_progress(self, operation, percent, info="", **kw):
        if operation == "fetching":
            file_name = kw["filename"]
            if not file_name.startswith("eopkg-index.xml"):
                file_name = pisi.util.parse_package_name(file_name)[0]
            out = (operation, file_name, str(percent), int(kw["rate"]), kw["symbol"], int(kw["downloaded_size"]), int(kw["total_size"]))
        else:
            out = (operation, str(percent), info, 0, 0, 0, 0)
        notify("System.Manager", "progress", out)

def _init_pisi():
    ui = UI()
    try:
        pisi.api.set_userinterface(ui)
    except KeyboardInterrupt:
        cancelled()

def _get_eopkg_config():
    if os.path.exists("/etc/eopkg/eopkg.conf"):
        return "/etc/eopkg/eopkg.conf"
    return "/usr/share/defaults/eopkg/eopkg.conf"

def cancelled():
    notify("System.Manager", "cancelled", None)

def started(operation=""):
   notify("System.Manager", "started", operation)

def finished(operation=""):
    if operation in ["System.Manager.setCache", "System.Manager.installPackage", "System.Manager.removePackage", "System.Manager.updatePackage"]:
        __checkCacheLimits()

    notify("System.Manager", "finished", operation)

def privileged(func):
    """
    Decorator for synchronizing privileged functions
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        operation = f"System.Manager.{func.__name__}"

        started(operation)
        _init_pisi()
        try:
            result = func(*args, **kwargs)
        except KeyboardInterrupt:
            cancelled()
            return
        except Exception as e:
            notify("System.Manager", "error", str(e))
            return
        finished(operation)
        return result

    return wrapper

@privileged
def installPackage(package=None):
    if package:
        package = package.split(",")
        reinstall = package[0].endswith(".eopkg")
        pisi.api.install(package, ignore_file_conflicts=True, reinstall=reinstall)

@privileged
def reinstallPackage(package=None):
    if package:
        package = package.split(",")
        pisi.api.install(package, ignore_file_conflicts=True, reinstall=True)

@privileged
def updatePackage(package=None):
    if package is None:
        package = []
    else:
        package = package.split(",")
    pisi.api.upgrade(package)

@privileged
def removePackage(package=None):
    if package:
        package = package.split(",")
        pisi.api.remove(package)

@privileged
def updateRepository(repository=None):
    if repository:
        pisi.api.update_repo(repository)

@privileged
def updateAllRepositories():
    repos = pisi.db.repodb.RepoDB().list_repos()
    for repo in repos:
        try:
            pisi.api.update_repo(repo)
        except pisi.db.repodb.RepoError as e:
            notify("System.Manager", "error", str(e))

@privileged
def addRepository(name=None,uri=None):
    if name and uri:
        pisi.api.add_repo(name,uri)

@privileged
def removeRepository(repo=None):
    if repo:
        pisi.api.remove_repo(repo)

@privileged
def setRepoActivities(repos=None):
    if repos:
        for repo, active in repos.items():
            pisi.api.set_repo_activity(repo, active)

@privileged
def setRepositories(repos):
    oldRepos = pisi.db.repodb.RepoDB().list_repos(only_active=False)

    for repo in oldRepos:
        pisi.api.remove_repo(repo)

    for repo in repos:
        pisi.api.add_repo(repo[0], repo[1])

@privileged
# ex: setConfig("general", "bandwidth_limit", "30")
def setConfig(category, name, value):
    config = pisi.configfile.ConfigurationFile("/etc/eopkg/eopkg.conf")
    config.set(category, name, value)

    config.write_config()

@privileged
def setCache(enabled, limit):
    config = pisi.configfile.ConfigurationFile("/etc/eopkg/eopkg.conf")
    config.set("general", "package_cache", str(enabled))
    config.set("general", "package_cache_limit", str(limit))

    config.write_config()

@privileged
def takeSnapshot():
    pisi.api.snapshot()

@privileged
def takeBack(operation):
    pisi.api.takeback(operation)

@privileged
def clearCache(cacheDir, limit):
    pisi.api.clearCache(int(limit) == 0)

def __checkCacheLimits():
    cached_pkgs_dir = "/var/cache/eopkg/packages"
    config = pisi.configfile.ConfigurationFile(_get_eopkg_config())
    cache = config.get("general", "package_cache")
    if cache == "True":
        limit = config.get("general", "package_cache_limit")

        # If PackageCache is used and limit is 0. It means limitless.
        if limit and int(limit) != 0:
            clearCache(cached_pkgs_dir, int(limit) * 1024 * 1024)
    elif cache == "False":
        clearCache(cached_pkgs_dir, 0)
