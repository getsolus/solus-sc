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

import os.path


class OsRelease:

    mapping = None

    def __init__(self):
        self.mapping = dict()
        paths = [
            "/etc/os-release",
            "/usr/lib64/os-release",
            "/usr/lib/os-release",
        ]
        # Follow paths in stateless order
        for p in paths:
            if not os.path.exists(p):
                continue
            try:
                self._parse_blob(p)
                break
            except Exception as e:
                print(e)
                continue

    def _parse_blob(self, path):
        """ Read the key/value sh-source syntax os-release file. It might
            break typical INI constraints so we can't use ConfigObj here """
        with open(path, "r") as inblob:
            for line in inblob.readlines():
                line = line.strip()
                if '=' not in line:
                    continue
                splits = line.split('=')
                key = splits[0]
                val = '='.join(splits[1:]).strip()
                if val.startswith('"'):
                    val = val[1:]
                if val.endswith('"'):
                    val = val[0:-1]
                self.mapping[key.lower()] = val

    def _keyval(self, key, fallback=""):
        """ Simple helper to not panic when reading a value """
        if key not in self.mapping:
            return fallback
        return self.mapping[key]

    def id(self):
        """ Return the main os-family """
        return self._keyval("id", "<unknown OS type>")

    def id_like(self):
        """ Return the ID_LIKE field """
        return self._keyval("id_like", "<unknown OS type>")

    def from_family(self, family):
        """ Return True if the OS is from the given family """
        if self.id() == family:
            return True
        if self.id_like() == family:
            return True
        return False

    def pretty_name(self):
        return self._keyval("pretty_name", "<unknown OS>")

    def version_id(self):
        return self._keyval("version_id")

    def version(self):
        return self._keyval("version")

    def name(self):
        """ Return the OS name """
        return self._keyval("name")

    def home_url(self):
        """ Return the homepage """
        return self._keyval("home_url", None)

    def support_url(self):
        """ Return the main support URL """
        return self._keyval("support_url", None)

    def bug_report_url(self):
        """ Return the bug report URL """
        return self._keyval("bug_report_url", None)
