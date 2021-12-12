#!/usr/bin/env python2
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
PHAB_URI = "https://dev.getsol.us"

# I know, it's evil. From:
# http://daringfireball.net/2010/07/improved_regex_for_matching_urls (2014 updated version)
GENERAL_URI = re.compile(r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.]\
(?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro\
|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh\
|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy\
|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi\
|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo\
|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk\
|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe\
|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl\
|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug\
|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*\
?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\
\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|\
gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|\
ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br\
|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm\
|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr\
|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km\
|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq\
|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm\
|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st\
|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc\
|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))""")

MARKUP_URI_HIT = re.compile(r"\[({})\]\(({})\)".format("[^\]]+", "[^)]+"))
MARKUP_CODE_HIT = re.compile(r"`([^`]+)`")
MARKUP_BOLD_HIT = re.compile(r"\*{2}([^\*{2}]+)\*{2}")


class ScChangelogEntry(Gtk.EventBox):

    def decode_changelog(self, text):
        ret = ""

        block_elems = [
            "Summary",
            "Test Plan",
            "Maniphest Tasks",
        ]
        block_elem_ids = ["{}:".format(x) for x in block_elems]

        # Iterate all the lines
        for r in text.split("\n"):
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
            r = CVE_HIT.sub(r' <a href="{}\1">\1</a>'.format(CVE_URI), r)
            r = BUG_HIT.sub(r' <a href="{}/T\1">T\1</a>'.format(PHAB_URI), r)
            r = DIFF_HIT.sub(r' <a href="{}/D\1">D\1</a>'.format(PHAB_URI), r)

            # Check if this is a bullet point
            if (r.startswith("- ") or r.startswith("* ")) and len(r) > 2:
                r = u' \u2022 ' + r[2:]
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
