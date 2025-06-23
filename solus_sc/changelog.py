#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2020 Solus
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk, GLib, GObject, Pango

import re

from . import PACKAGE_ICON_NORMAL
from . import PACKAGE_ICON_SECURITY

# Helpful for determing CVE matches.
CVE_HIT = re.compile(r" (CVE\-[0-9]+\-[0-9]+)")
CVE_URI = "https://cve.mitre.org/cgi-bin/cvename.cgi?name="

# All TNNNN hits are Maniphest Tasks, DNNNN are Differential Revisions
BUG_HIT = re.compile(r" T(\d+)")
DIFF_HIT = re.compile(r" D(\d+)")
GITHUB_ISSUE_HIT = re.compile(r"#(\d+)")
PHAB_URI = "https://dev.getsol.us"
GITHUB_URI = "https://github.com/getsolus/packages"

# I know, it's evil. From:
# http://daringfireball.net/2010/07/improved_regex_for_matching_urls
GENERAL_URI = re.compile(r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d\
{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)\
))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>\
?«»“”‘’]))""")

MARKUP_URI_HIT = re.compile(r"\[({})\]\(({})\)".format("[^\]]+", "[^)]+"))
MARKUP_CODE_HIT = re.compile(r"`([^`]+)`")
MARKUP_CODE_BLOCK_HIT = re.compile(r"```(\r\n|\r|\n)([^`]+)```")
MARKUP_BOLD_HIT = re.compile(r"\*{2}([^\*{2}]+)\*{2}")
MARKUP_ITALIC_HIT = re.compile(r"^_([^_]+)_| _([^_]+)_")
MARKUP_COMMENT_HIT = re.compile(r"&lt;!--.*--&gt;")
MARKUP_GITHUB_CHECKED_TASK_HIT = re.compile(r"- \[x\](.*)")
MARKUP_GITHUB_UNCHECKED_TASK_HIT = re.compile(r"- \[ \](.*)")
MARKUP_GITHUB_TITLE_HIT = re.compile(r"[#]+ ([^#]+)")
GIT_SIGNED_OFF_BY_LINE = "Signed-off-by:"
MARKUP_SIGNED_OFF_BY_HIT = re.compile(r"{} (.*)".format(GIT_SIGNED_OFF_BY_LINE))


class ScChangelogEntry(Gtk.EventBox):

    def decode_changelog(self, text):
        ret = ""

        block_elems = [
            "Summary",
            "Test Plan",
            "Maniphest Tasks",
        ]
        block_elem_ids = ["{}:".format(x) for x in block_elems]

        text = MARKUP_CODE_BLOCK_HIT.sub(r'<tt>\2</tt>', text)

        # Iterate all the lines
        for r in text.split("\n"):
            # Skip this line early if it's an HTML comment
            if MARKUP_COMMENT_HIT.match(r):
                continue

            # Save number of leading spaces for bullet point indentation
            lspaces = len(r) - len(r.lstrip())
            r = r.strip()

            # Handle Differential IDs by stylizing them
            for i, id in enumerate(block_elem_ids):
                if not r.startswith(id):
                    continue
                ret += "<b><u>{}</u></b>\n".format(block_elems[i])
                r = r.split(id)[1].strip()
                break

            r = MARKUP_URI_HIT.sub(r'<a href="\2">\1</a>', r)
            r = MARKUP_CODE_HIT.sub(r'<tt>\1</tt>', r)
            r = MARKUP_BOLD_HIT.sub(r'<b>\1</b>', r)
            r = MARKUP_ITALIC_HIT.sub(r'<i>\1</i>', r)
            r = MARKUP_GITHUB_CHECKED_TASK_HIT.sub(r'&#x1F5F9; \1', r)
            r = MARKUP_GITHUB_UNCHECKED_TASK_HIT.sub(r'&#x2610; \1', r)
            r = MARKUP_GITHUB_TITLE_HIT.sub(r'<i>\1</i>\n', r)
            r = MARKUP_SIGNED_OFF_BY_HIT.sub(r'<small><b>{}</b> <i>\1</i></small>'.format(GIT_SIGNED_OFF_BY_LINE), r)
            r = CVE_HIT.sub(r' <a href="{}\1">\1</a>'.format(CVE_URI), r)
            r = BUG_HIT.sub(r' <a href="{}/T\1">T\1</a>'.format(PHAB_URI), r)
            r = DIFF_HIT.sub(r' <a href="{}/D\1">D\1</a>'.format(PHAB_URI), r)
            r = GITHUB_ISSUE_HIT.sub(r'<a href="{}/issues/\1">#\1</a>'.format(GITHUB_URI), r)

            # Check if this is a bullet point
            if (r.startswith("- ") or r.startswith("* ")) and len(r) > 2:
                r = ' \u2022 ' + r[2:]
                # add a tab for every indentation level
                while (lspaces > 0):
                    r = "\t" + r
                    lspaces -= 1

            for i in r.split(" "):
                uri = GENERAL_URI.match(i)
                if uri is not None:
                    uri_href = uri.group(0)
                    href = "<a href=\"{}\">{}</a>".format(uri_href, uri_href)
                    ret += href + i[len(uri_href):] + " "
                    continue
                # Just add the text
                ret += i + " "
                continue

            ret += "\n"
        return ret.strip()

    def __init__(self, obj, history):
        Gtk.EventBox.__init__(self)
        self.get_style_context().add_class("changelog-entry")

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        top_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        top_box.set_property("margin", 12)
        top_box.get_style_context().add_class("changelog-header")
        self.add(vbox)
        vbox.pack_start(top_box, False, False, 0)

        # format name to correlate with git entry.
        nom = "{}-{}".format(history.version, history.release)

        text = GLib.markup_escape_text(str(history.comment))

        iname = PACKAGE_ICON_NORMAL
        up_type = str(history.type).lower()
        tooltip = _("Standard Update")
        if up_type == "security":
            iname = PACKAGE_ICON_SECURITY
            tooltip = _("Security Update")

        image = Gtk.Image.new_from_icon_name(iname, Gtk.IconSize.BUTTON)
        image.set_valign(Gtk.Align.END)
        top_box.pack_end(image, False, False, 0)
        image.set_margin_end(8)
        image.set_margin_bottom(8)
        image.set_tooltip_text(tooltip)

        main_lab = Gtk.Label("<b>%s</b>" % nom)
        main_lab.set_margin_bottom(8)
        main_lab.set_use_markup(True)
        main_lab.set_halign(Gtk.Align.START)
        main_lab.set_valign(Gtk.Align.START)
        main_lab.set_property("xalign", 0.0)

        top_box.pack_start(main_lab, False, False, 0)

        # Add the summary, etc.
        sum_lab = Gtk.Label(self.decode_changelog(text))
        sum_lab.set_halign(Gtk.Align.START)
        sum_lab.set_valign(Gtk.Align.START)
        sum_lab.set_property("margin-start", 14)
        sum_lab.set_property("margin-end", 14)
        sum_lab.set_property("margin-bottom", 14)
        sum_lab.set_use_markup(True)
        sum_lab.set_line_wrap_mode(Pango.WrapMode.WORD)
        sum_lab.set_line_wrap(True)
        sum_lab.set_property("xalign", 0.0)
        sum_lab.set_max_width_chars(85)
        sum_lab.set_width_chars(80)
        vbox.pack_start(sum_lab, True, True, 0)

        # Timestamp is kinda useful.
        tstamp = Gtk.Label("({})".format(str(history.date)))
        tstamp.set_valign(Gtk.Align.START)
        top_box.pack_start(tstamp, False, False, 0)
        tstamp.get_style_context().add_class("dim-label")
        tstamp.set_margin_start(8)
        tstamp.set_margin_bottom(8)

        self.show_all()


class ScUpdateObject(GObject.Object):
    """ Keep glib happy and allow us to store references in a liststore """

    old_pkg = None
    new_pkg = None

    # Simple, really.
    has_security_update = False

    __gtype_name__ = "ScUpdateObject"

    def __init__(self, old_pkg, new_pkg):
        GObject.Object.__init__(self)
        self.old_pkg = old_pkg
        self.new_pkg = new_pkg

        if not self.old_pkg:
            return
        oldRelease = int(self.old_pkg.release)
        histories = self.get_history_between(oldRelease, self.new_pkg)

        # Initial security update detection
        securities = [x for x in histories if x.type == "security"]
        if len(securities) < 1:
            return
        self.has_security_update = True

    def get_update_size(self):
        """ Determine the update size for a given package """
        # FIXME: Check pisi config
        deltasEnabled = True

        pkgSize = self.new_pkg.packageSize
        if not deltasEnabled:
            return pkgSize
        if not self.old_pkg:
            return pkgSize
        delt = self.new_pkg.get_delta(int(self.old_pkg.release))
        """ No delta available. """
        if not delt:
            return pkgSize
        return delt.packageSize

    def is_security_update(self):
        """ Determine if the update introduces security fixes """
        return self.has_security_update

    def get_history_between(self, old_release, new):
        """ Get the history items between the old release and new pkg """
        ret = list()

        for i in new.history:
            if int(i.release) <= int(old_release):
                continue
            ret.append(i)
        ret.sort(key=lambda x: int(x.release), reverse=True)
        return ret
