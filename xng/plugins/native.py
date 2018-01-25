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

from .os_release import OsRelease


_native_plugin = None
_unsupported = None
_os_release = None


def get_os_release():
    """ Cache an OsRelease instance to prevent any future re-reads """
    global _os_release

    if _os_release is not None:
        return _os_release
    _os_release = OsRelease()
    return _os_release


def get_native_plugin():
    global _native_plugin
    global _unsupported

    """ Attempt to grab the native system plugin """
    if _native_plugin is not None:
        return _native_plugin
    if _unsupported:
        return None

    osRel = get_os_release()
    if osRel.from_family("solus"):
        from .eopkg import EopkgPlugin
        _native_plugin = EopkgPlugin()
        return _native_plugin

    _unsupported = True
    return None
