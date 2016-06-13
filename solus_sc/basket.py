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

import gi.repository
from gi.repository import Gtk, GObject

import comar
import pisi.db
from pisi.operations.install import plan_install_pkg_names
from pisi.operations.remove import plan_remove
from pisi.operations.upgrade import plan_upgrade
from widgets import PackageLabel


class BasketView(Gtk.Revealer):

    __gsignals__ = {
        'basket-changed': (GObject.SIGNAL_RUN_FIRST, None, (object,)),
        'apply': (GObject.SIGNAL_RUN_FIRST, None,
                          (object,))
    }

    def __init__(self, packagedb, installdb):
        Gtk.Revealer.__init__(self)

        self.packagedb = packagedb
        self.installdb = installdb
        if not self.packagedb:
            self.packagedb = pisi.db.packagedb.PackageDB()
        if not self.installdb:
            self.installdb = pisi.db.installdb.InstallDB()

        self.title = Gtk.Label("Software basket")
        self.title.set_use_markup(True)

        self.layout = Gtk.VBox()

        self.progress = Gtk.ProgressBar()
        self.revealer = Gtk.Revealer()
        self.revealer.add(self.progress)
        self.layout.pack_start(self.revealer, False, False, 0)
        self.revealer.set_reveal_child(False)

        self.toolbar = Gtk.Toolbar()
        self.toolbar.get_style_context().add_class(
            Gtk.STYLE_CLASS_PRIMARY_TOOLBAR)
        label_item = Gtk.ToolItem()
        label_item.add(self.title)
        self.toolbar.add(label_item)

        self.layout.pack_start(self.toolbar, False, False, 0)

        self.add(self.layout)
        sep = Gtk.SeparatorToolItem()
        sep.set_expand(True)
        sep.set_draw(False)
        self.toolbar.add(sep)

        self.apply = Gtk.ToolButton("Apply")
        self.apply.set_label("Apply")
        self.apply.set_is_important(True)
        self.apply.set_icon_name("emblem-ok-symbolic")
        self.apply.connect("clicked", self.apply_operations)
        self.toolbar.add(self.apply)
        self.operations = dict()

        self.update_ui()

        self.cb = None
        self.link = comar.Link()
        self.pmanager = self.link.System.Manager['pisi']
        self.link.listenSignals("System.Manager", self.pisi_callback)

        self.current_operations = None

        self.downloaded = 0
        self.current_package = None

    def set_progress(self, fraction, label):
        if fraction is None:
            # Hide
            self.revealer.set_reveal_child(False)
            self.update_ui()
            return
        # print "%s %f" % (label, fraction)
        self.title.set_markup(label)
        self.revealer.set_reveal_child(True)
        self.progress.set_fraction(fraction)

    def update_ui(self):
        count = self.operation_count()
        if count == 0:
            self.apply.set_sensitive(False)
            self.set_reveal_child(False)
            return
        self.apply.set_sensitive(True)
        if count > 1:
            self.title.set_markup("{} operations pending".format(
                self.operation_count()))
        else:
            self.title.set_markup("One operation pending")
        self.set_reveal_child(True)

    def operation_for_package(self, package):
        if package.name in self.operations:
            return self.operations[package.name]
        return None

    def operation_count(self):
        return len(self.operations)

    def operation_count_type(self, type):
        return len([x for x in self.operations if self.operations[x] == type])

    def forget_package(self, package):
        if package.name in self.operations:
            self.operations.pop(package.name, None)
        self.update_ui()

    def remove_package(self, old_package):
        self.operations[old_package.name] = 'UNINSTALL'
        self.update_ui()

    def install_package(self, new_package):
        self.operations[new_package.name] = 'INSTALL'
        self.update_ui()

    def update_package(self, old_package, new_package):
        self.operations[old_package.name] = 'UPDATE'
        self.update_ui()

    def _get_prog(self, step):
        self.progress_current = step
        total = float(self.progress_total)
        current = float(self.progress_current)

        fract = float(current/total)
        return fract

    def pisi_callback(self, package, signal, args):
        if signal == 'status':
            cmd = args[0]
            what = args[1]
            if cmd == 'updatingrepo':
                self.set_progress(1.0, "Updating %s repository" % what)
            elif cmd == 'extracting':
                prog = self._get_prog(self.progress_current + self.step_offset)
                msg = "Extracting {} of {}: {}".format(
                    self.current_package, self.total_packages, what)
                self.set_progress(prog, msg)
            elif cmd == 'configuring':
                prog = self._get_prog(self.progress_current + self.step_offset)
                msg = "Configuring {} of {}: {}".format(
                    self.current_package, self.total_packages, what)
                self.set_progress(prog, msg)
            elif cmd in ['removing', 'installing']:
                prog = self._get_prog(self.progress_current + self.step_offset)
                lab = "Installing %s: %s"
                if cmd == 'removing':
                    lab = "Removing %s: %s"
                count = "{} of {}".format(
                    self.current_package, self.total_packages)
                self.set_progress(prog, lab % (count, what))
            elif cmd in ['upgraded', 'installed', 'removed']:
                prog = self._get_prog(self.progress_current + self.step_offset)
                if cmd == 'upgraded':
                    lab = "Upgraded %s: %s"
                elif cmd == 'removed':
                    lab = "Removed %s: %s"
                elif cmd == 'installed':
                    lab = "Installed %s: %s"
                count = "{} of {}".format(
                    self.current_package,
                    self.total_packages)
                self.set_progress(prog, lab % (count, what))
                self.current_package += 1

        if signal == 'progress':
            cmd = args[0]
            if cmd == 'fetching':
                if self.current_operations is not None:
                    # Doing real operations now.
                    package = args[1]
                    whatisthis = args[2]
                    speed_number = args[3]
                    speed_label = args[4]
                    downloaded = args[5]
                    download_size = args[6]
                    down = downloaded
                    speed = "%d %s" % (speed_number, speed_label)

                    diff = downloaded - download_size
                    inc = self.total_size + diff
                    prog = self._get_prog(inc)

                    disp = "Downloading {} of {}: {} ({})"
                    self.set_progress(prog, disp.format(
                            self.current_dl_package,
                            self.total_packages, package, speed))

                    if downloaded >= download_size:
                        self.current_dl_package += 1
                else:
                    # print args
                    self.set_progress(1.0, "Downloading %s" % args[1])
        elif signal == 'finished' or signal is None:
            if self.cb is not None:
                self.cb()
            self.cb = None
            self.set_progress(None, None)
            self.update_ui()
            return

    def update_repo(self, cb=None):
        self.cb = cb
        self.pmanager.updateAllRepositories()

    def get_sizes(self, packages):
        totalSize = 0
        packages = [self.packagedb.get_package(pkg) for pkg in packages]
        for package in packages:
            totalSize += package.packageSize
        return totalSize

    def invalidate_all(self):
        # Handle operations that finished.
        print("HAPPEND!")
        self.operations = dict()
        self.emit('basket-changed', None)
        pisi.db.invalidate_caches()
        self.installdb = pisi.db.installdb.InstallDB()
        self.packagedb = pisi.db.packagedb.PackageDB()
        self.componentdb = pisi.db.componentdb.ComponentDB()
        self.groupdb = pisi.db.groupdb.GroupDB()

    def show_dialog(self, pkgs, remove=False, update=False, install=True):
        markup = "<big>{}</big>".format(
            "The following packages need to be installed to continue")

        flags = Gtk.DialogFlags.MODAL | Gtk.DialogFlags.USE_HEADER_BAR
        dlg = Gtk.MessageDialog(self.get_toplevel(),
                                flags,
                                Gtk.MessageType.QUESTION,
                                Gtk.ButtonsType.OK_CANCEL)

        dlg = Gtk.Dialog(use_header_bar=1)
        dlg.set_title("Installation confirmation")
        if remove:
            markup = "<big>The following packages need to be removed to " \
                     "continue</big>"
            dlg.set_title("Removal confirmation")
        elif update:
            markup = "<big>The following packages need to be updated to " \
                     "continue</big>"
            dlg.set_title("Update confirmation")

        lab = Gtk.Label(markup)
        lab.set_use_markup(True)
        box = Gtk.HBox(0)
        box.set_property("margin", 5)
        box.pack_start(lab, True, True, 0)
        dlg.get_content_area().pack_start(box, False, False, 0)
        dlg.get_content_area().set_border_width(5)
        dlg.get_action_area().set_border_width(5)

        scroll = Gtk.ScrolledWindow(None, None)
        lbox = Gtk.ListBox()
        scroll.add(lbox)
        scroll.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scroll.set_property("margin", 5)

        for pkg in pkgs:
            if remove:
                package = self.installdb.get_package(pkg)
            else:
                package = self.packagedb.get_package(pkg)
            panel = PackageLabel(package, None, interactive=False)
            lbox.add(panel)
        dlg.get_content_area().pack_start(scroll, True, True, 0)
        dlg.get_content_area().show_all()

        btn = dlg.add_button("Cancel", Gtk.ResponseType.CANCEL)
        if not remove:
            btn = dlg.add_button("Install" if install else "Update",
                                 Gtk.ResponseType.OK)
            btn.get_style_context().add_class("suggested-action")
        else:
            btn = dlg.add_button("Remove", Gtk.ResponseType.OK)
            btn.get_style_context().add_class("destructive-action")
        dlg.set_default_size(250, 400)
        res = dlg.run()
        dlg.destroy()
        if res == Gtk.ResponseType.OK:
            return True
        return False

    def apply_operations(self, btn):
        updates = [
            i for i in self.operations if self.operations[i] == 'UPDATE'
        ]
        installs = [
            i for i in self.operations if self.operations[i] == 'INSTALL'
        ]
        removals = [
            i for i in self.operations if self.operations[i] == 'UNINSTALL'
        ]

        # We monitor 4 post events
        STEPS = 4

        self.installdb = pisi.db.installdb.InstallDB()
        self.packagedb = pisi.db.packagedb.PackageDB()

        self.emit('apply', None)
        # print "%d packages updated" % len(updates)
        # print "%d packages installed" % len(installs)
        # print "%d packages removed" % len(removals)

        setAct = False

        for packageset in [updates, installs, removals]:
            if len(packageset) == 0:
                continue

            self.current_package = 1
            self.current_dl_package = 1

            if packageset == installs:
                (pg, pkgs) = plan_install_pkg_names(packageset)
                if len(pkgs) > len(packageset):
                    if self.show_dialog(pkgs):
                        installs = packageset = pkgs
                    else:
                        # print "Not installing"
                        continue
            elif packageset == removals:
                (pk, pkgs) = plan_remove(packageset)
                if len(pkgs) > len(packageset):
                    if self.show_dialog(pkgs, remove=True):
                        removals = packageset = pkgs
                    else:
                        # print "Not removing"
                        continue
            elif packageset == removals:
                (pk, pkgs) = plan_upgrade(packageset)
                if len(pkgs) > len(packageset):
                    if self.show_dialog(pkgs, update=True):
                        updates = packageset = pkgs
                    else:
                        # print Not continuing
                        continue
            self.total_packages = len(packageset)
            setAct = True

            if packageset != removals:
                self.total_size = self.get_sizes(packageset)
                # one tenth of progress is post install
                self.step_offset = self.total_size / 10
                self.progress_total = self.total_size + \
                    ((self.step_offset * self.total_packages) * STEPS)
            else:
                self.total_size = self.total_packages * (STEPS / 2)
                self.step_offset = 1
                self.progress_total = self.total_size
            self.progress_current = 0

            self.current_operations = packageset

            self.cb = self.invalidate_all
            if packageset == updates:
                self.pmanager.updatePackage(
                    ",".join(packageset), async=self.pisi_callback)
            elif packageset == installs:
                self.pmanager.installPackage(
                    ",".join(packageset), async=self.pisi_callback)
            elif packageset == removals:
                self.pmanager.removePackage(
                    ",".join(packageset), async=self.pisi_callback)
        if not setAct:
            self.invalidate_all()
            self.update_ui()
