#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2013-2017 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk, GLib
from plugins.base import PopulationFilter

class GroupButton(Gtk.Button):
    """ Manage the monotony of a Group """

    group = None

    def __init__(self, group):
        Gtk.Button.__init__(self)

        self.group = group

        icon_theme = self.get_settings().get_property("gtk-icon-theme-name")
        icon_theme = icon_theme.lower().replace("-", "")
        # Sneaky, I know.
        if icon_theme == "arcicons" or icon_theme == "arc":
            devIcon = "text-x-changelog"
        else:
            devIcon = "gnome-dev-computer"

        replacements = {
            "text-editor": "x-office-calendar",
            "redhat-programming": devIcon,
            "security-high": "preferences-system-privacy",
            "network": "preferences-system-network",
        }

        # Pretty things up with a Icon|Label setup
        icon = group.get_icon_name()
        if icon in replacements:
            icon = replacements[icon]

        gDesc = GLib.markup_escape_text(group.get_name())
        image = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DIALOG)
        image.set_pixel_size(64)
        image.set_halign(Gtk.Align.START)

        label_box = Gtk.VBox(0)
        label_box.set_valign(Gtk.Align.CENTER)

        box = Gtk.HBox(0)
        box.pack_start(image, False, False, 0)
        image.set_property("margin-right", 10)
        label = Gtk.Label("<big>{}</big>".format(gDesc))
        label.set_use_markup(True)
        label.get_style_context().add_class("title")
        label.set_halign(Gtk.Align.START)
        label.set_valign(Gtk.Align.START)
        label_box.pack_start(label, True, True, 0)
        box.pack_start(label_box, True, True, 0)
        self.add(box)

        self.get_style_context().add_class("flat")

        # count the components
        nkids = len(group.get_children())
        # "5 categories" - the number of categories within each group
        info_label = Gtk.Label(_("{} categories").format(nkids))
        info_label.set_halign(Gtk.Align.START)
        info_label.get_style_context().add_class("info-label")
        info_label.get_style_context().add_class("dim-label")
        label_box.pack_start(info_label, False, False, 0)

        self.get_style_context().add_class("group-button")
        
class HomeView(Gtk.Box):
    """ Main home view - shows a repo activity feed with the root level
        category switcher """

    # Our next_sc plugin set
    plugins = None

    # Our appsystem for resolving metadata
    appsystem = None

    box_new = None
    box_recent = None
    box_group = None

    flowbox_groups = None

    def __init__(self, appsystem, plugins):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.appsystem = appsystem
        self.plugins = plugins
        self.box_group = Gtk.SizeGroup.new(Gtk.SizeGroupMode.BOTH)
        self.set_margin_start(20)
        self.set_margin_end(20)

        lab = Gtk.Label.new("<big>{}</big>".format(_("New software")))
        lab.set_margin_start(6)
        lab.set_margin_top(6)
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.START)
        self.pack_start(lab, False, False, 0)
        self.box_new = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        scroll = Gtk.ScrolledWindow.new(None, None)
        scroll.set_margin_top(6)
        scroll.set_margin_bottom(12)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        scroll.add(self.box_new)
        self.pack_start(scroll, False, False, 0)

        lab = Gtk.Label.new("<big>{}</big>".format(_("Recently updated")))
        lab.set_margin_start(6)
        lab.set_margin_top(6)
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.START)
        self.pack_start(lab, False, False, 0)
        self.box_recent = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)

        scroll = Gtk.ScrolledWindow.new(None, None)
        scroll.set_margin_top(6)
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.NEVER)
        scroll.add(self.box_recent)
        self.pack_start(scroll, False, False, 0)

        # find out about new shinies
        for p in self.plugins:
            p.populate_storage(self, PopulationFilter.NEW, self.appsystem)
            p.populate_storage(self, PopulationFilter.RECENT, self.appsystem)


        # Fix up categories
        lab = Gtk.Label.new("<big>{}</big>".format(_("Categories")))
        lab.set_margin_start(6)
        lab.set_margin_top(36)
        lab.set_margin_bottom(12)
        lab.set_use_markup(True)
        lab.set_halign(Gtk.Align.START)
        self.pack_start(lab, False, False, 0)

        self.build_categories()

    def build_categories(self):
        """ Build up a flowbox allowing navigation to different categories """
        self.flowbox_groups = Gtk.FlowBox()
        self.flowbox_groups.set_min_children_per_line(3)
        self.flowbox_groups.set_property("margin", 20)
        self.flowbox_groups.set_column_spacing(30)
        self.flowbox_groups.set_row_spacing(15)
        self.flowbox_groups.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.flowbox_groups.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox_groups.set_valign(Gtk.Align.START)
        self.pack_start(self.flowbox_groups, False, False, 0)
        for p in self.plugins:
            for cat in p.categories():
                btn = GroupButton(cat)
                self.flowbox_groups.add(btn)
                btn.show_all()

    def clear(self):
        """ Clear any custom stuff from the home view """
        for child in box_new.get_children():
            child.destroy()
        for child in box_recent.get_children():
            child.destroy()

    def add_item(self, id, item, popfilter):
        """ Handle adding items to our view """
        target = None
        if popfilter == PopulationFilter.NEW:
            target = self.box_new
        elif popfilter == PopulationFilter.RECENT:
            target = self.box_recent
        else:
            return

        pbuf = self.appsystem.get_pixbuf(id)
        img = Gtk.Image.new_from_pixbuf(pbuf)
        img.set_margin_end(8)
        btnText = self.appsystem.get_name(id, item.get_title())
        summary = self.appsystem.get_summary(id, item.get_summary())
        if len(summary) > 30:
            summary = "%s…" % summary[0:30]
        btnText = "<b>{}</b>\n{}".format(btnText, summary)
        btn = Gtk.Button.new()
        box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        box.pack_start(img, False, False, 0)
        lab = Gtk.Label.new(btnText)
        lab.set_halign(Gtk.Align.START)
        lab.set_use_markup(True)
        box.pack_start(lab, False, False, 0)
        btn.add(box)
        btn.show_all()
        btn.set_margin_top(6)
        btn.set_margin_bottom(6)
        btn.set_margin_start(3)
        btn.set_margin_end(3)
        self.box_group.add_widget(btn)
        target.pack_start(btn, False, False, 0)
