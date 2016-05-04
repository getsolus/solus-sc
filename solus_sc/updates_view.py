#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  This file is part of solus-sc
#
#  Copyright © 2014-2016 Ikey Doherty <ikey@solus-project.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#

from gi.repository import Gtk, GLib, GdkPixbuf
from pisi.db.packagedb import PackageDB
from pisi.db.installdb import InstallDB
from . import sc_format_size

import pisi.api


PACKAGE_ICON_SECURITY = "security-high-symbolic"
PACKAGE_ICON_NORMAL = "software-update-available-symbolic"
PACKAGE_ICON_MANDATORY = "software-update-urgent-symbolic"


class ScUpdatesView(Gtk.VBox):

    installdb = None
    packagedb = None
    tview = None

    toolbar = None
    selection_label = None

    def __init__(self):
        Gtk.VBox.__init__(self, 0)

        self.scroll = Gtk.ScrolledWindow(None, None)
        self.scroll.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        self.scroll.set_overlay_scrolling(False)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scroll.set_property("kinetic-scrolling", True)
        self.pack_start(self.scroll, True, True, 0)

        # Junction bottom for toolbar join
        st = self.scroll.get_style_context()
        st.set_junction_sides(Gtk.JunctionSides.BOTTOM)

        self.tview = Gtk.TreeView()
        self.tview.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.scroll.add(self.tview)
        self.tview.set_property("enable-grid-lines", False)
        self.tview.set_property("headers-visible", False)

        # Can toggle?
        ren = Gtk.CellRendererToggle()
        ren.set_activatable(True)
        ren.connect('toggled', self.on_toggled)
        ren.set_padding(5, 5)
        ren.set_property("xalign", 1.0)
        column = Gtk.TreeViewColumn("Install?", ren, active=0,
                                    activatable=1, sensitive=5)
        self.tview.append_column(column)

        ren = Gtk.CellRendererPixbuf()
        ren.set_padding(5, 5)
        column = Gtk.TreeViewColumn("Type", ren, icon_name=4, sensitive=5)
        self.tview.append_column(column)
        ren.set_property("stock-size", Gtk.IconSize.DIALOG)

        # Label of top row
        text_ren = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Label", text_ren, markup=2, sensitive=5)
        text_ren.set_padding(5, 5)
        self.tview.append_column(column)

        # Update size
        text_ren = Gtk.CellRendererText()
        text_ren.set_property("xalign", 1.0)
        column = Gtk.TreeViewColumn("Size", text_ren, text=3, sensitive=5)
        self.tview.append_column(column)

        # Main toolbar
        self.toolbar = Gtk.Toolbar()
        st = self.toolbar.get_style_context()
        st.set_junction_sides(Gtk.JunctionSides.TOP)
        st.add_class(Gtk.STYLE_CLASS_INLINE_TOOLBAR)
        st.add_class("update-toolbar")
        self.pack_end(self.toolbar, False, False, 0)

        # Selection label
        self.selection_label = Gtk.Label("0 items selected")
        titem = Gtk.ToolItem()
        titem.set_property("margin-start", 6)
        titem.add(self.selection_label)
        self.toolbar.add(titem)

        # Right align the toolbar
        sep = Gtk.SeparatorToolItem()
        sep.set_draw(False)
        sep.set_expand(True)
        self.toolbar.add(sep)

        # View details, i.e. changelog
        view_details = Gtk.ToolButton(None, None)
        view_details.set_sensitive(False)
        view_details.set_property("label", "View Details")
        view_details.set_property("icon-name", "view-list-details-symbolic")
        view_details.set_is_important(True)
        self.toolbar.add(view_details)
        GLib.idle_add(self.init_view)

    def on_toggled(self, w, path):
        model = self.tview.get_model()
        model[path][0] = not model[path][0]

    def get_history_between(self, old_release, new):
        """ Get the history items between the old release and new pkg """
        ret = list()

        for i in new.history:
            if i.release <= old_release:
                continue
            ret.append(i)
        return ret

    def get_update_size(self, oldPkg, newPkg):
        """ Determine the update size for a given package """
        # FIXME: Check pisi config
        deltasEnabled = True

        pkgSize = newPkg.packageSize
        if not deltasEnabled:
            return pkgSize
        if not oldPkg:
            return pkgSize
        delt = newPkg.get_delta(int(oldPkg.release))
        """ No delta available. """
        if not delt:
            return pkgSize
        return delt.packageSize

    def init_view(self):
        # Install? Modifiable? Display label | Size | Image | Sensitive | iSize
        model = Gtk.TreeStore(bool, bool, str, str, str, bool, int)

        # Mandatory updates
        m_label = "<b>Required updates</b>\n" \
                  "These updates are mandatory and will be selected " \
                  "automatically."
        row_m = model.append(None, [True, False, m_label, None,
                                    PACKAGE_ICON_MANDATORY, True, 0])
        # Security row
        s_label = "<b>Security Updates</b>\n" \
                  "These updates are strongly recommended to support safe " \
                  "usage of your device."
        row_s = model.append(None, [False, True, s_label, None,
                                    PACKAGE_ICON_SECURITY, True, 0])
        # All other updates
        u_label = "<b>Other Updates</b>\n" \
                  "These updates may introduce new software versions and " \
                  "bug-fixes."
        row_u = model.append(None, [False, True, u_label, None,
                                    PACKAGE_ICON_NORMAL, True, 0])

        self.tview.set_model(model)

        # Need a shared context for these guys
        self.installdb = InstallDB()
        self.packagedb = PackageDB()

        # Expand with a plan operation to be up front about new deps
        upgrades = pisi.api.list_upgradable()

        for item in sorted(upgrades):
            new_pkg = self.packagedb.get_package(item)
            new_version = "%s-%s" % (str(new_pkg.version),
                                     str(new_pkg.release))
            pkg_name = str(new_pkg.name)
            old_pkg = None
            old_version = "Not installed"
            systemBase = False
            oldRelease = 0

            icon = PACKAGE_ICON_NORMAL
            if new_pkg.partOf == "system.base":
                systemBase = True
                parent_row = row_m
            else:
                parent_row = row_u

            if self.installdb.has_package(item):
                old_pkg = self.installdb.get_package(item)
                old_version = "%s-%s" % (str(old_pkg.version),
                                         str(old_pkg.release))
                oldRelease = int(old_pkg.release)

            histories = self.get_history_between(oldRelease, new_pkg)
            # Initial security update detection
            securities = [x for x in histories if x.type == "security"]
            if len(securities) > 0:
                parent_row = row_s
                icon = PACKAGE_ICON_SECURITY

            summary = str(new_pkg.summary)
            if len(summary) > 76:
                summary = "%s…" % summary[0:76]

            # Finally, actual size, and readable size
            pkgSize = self.get_update_size(old_pkg, new_pkg)
            dlSize = "%.1f %s" % sc_format_size(pkgSize)

            icon = "package-x-generic"
            if new_pkg.icon is not None:
                icon = str(new_pkg.icon)

            p_print = "%s - <small>%s</small>\n%s" % (pkg_name,
                                                      new_version,
                                                      summary)
            model.append(parent_row, [systemBase, not systemBase,
                                      p_print, dlSize, icon, True, pkgSize])

            while (Gtk.events_pending()):
                Gtk.main_iteration()

        # Disable empty rows
        for item in [row_s, row_m, row_u]:
            if model.iter_n_children(item) == 0:
                model.set(item, 0, False)
                model.set(item, 1, False)
                model.set(item, 5, False)

        # Hook up events so we know what's going on (4 non blondes.)
        self.update_from_selection()
        model.connect_after('row-changed', self.on_model_row_changed)
        return False

    should_ignore = False

    def on_model_row_changed(self, tmodel, path, titer):
        """ Handle selection changes """
        parent = tmodel.iter_parent(titer)

        if self.should_ignore:
            return

        self.should_ignore = True

        # Handle child set to parent
        if parent is not None:
            num_children = tmodel.iter_n_children(parent)
            active_children = []
            inactive_children = []

            # Find all inactive checkboxes
            for i in xrange(0, num_children):
                child = tmodel.iter_nth_child(parent, i)
                child_path = tmodel.get_path(child)
                active = tmodel[child_path][0]
                if not active:
                    inactive_children.append(child_path)

            ppath = tmodel.get_path(parent)
            # One inactive means parent = FALSE, all active = TRUE
            if len(inactive_children) > 0:
                tmodel[ppath][0] = False
            else:
                tmodel[ppath][0] = True
        else:
            # Handle parent set children
            num_children = tmodel.iter_n_children(titer)
            active = tmodel[path][0]
            for i in xrange(0, num_children):
                child = tmodel.iter_nth_child(titer, i)
                child_path = tmodel.get_path(child)

                tmodel[child_path][0] = active

        self.should_ignore = False

        self.update_from_selection()

    """ Update selection, size, etc, from current view """
    def update_from_selection(self):
        model = self.tview.get_model()

        total_update = 0
        total_size = 0

        # enumerate root nodes
        for i in xrange(0, model.iter_n_children(None)):
            root_kid = model.iter_nth_child(None, i)

            # enumarate children in this root node
            for j in xrange(0, model.iter_n_children(root_kid)):
                child = model.iter_nth_child(root_kid, j)
                child_path = model.get_path(child)

                active = model[child_path][0]
                if not active:
                    continue
                total_update += 1
                total_size += model[child_path][6]
        # Skip it.
        if total_update == 0:
            self.selection_label.set_text("%s items selected" % total_update)
            return
        dlSize = "%.2f %s" % sc_format_size(total_size)
        newLabel = "%s items selected - (%s to download)" % \
                   (total_update, dlSize)
        self.selection_label.set_text(newLabel)
