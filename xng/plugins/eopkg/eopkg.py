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

from ..base import ProviderPlugin, ProviderItem, ProviderSource, \
    ProviderCategory
from ..base import PopulationFilter, ItemStatus, Transaction
from gi.repository import AppStreamGlib as As
from gi.repository import Gtk
import pisi
from pisi.operations.install import plan_install_pkg_names
from pisi.operations.remove import plan_remove, plan_autoremove
# from pisi.operations.upgrade import plan_upgrade
from pisi.operations import helper as pisi_helper
import time
import comar
import difflib


def find_have_data(adb, store):
    """ Find all packages with AppStream data """
    ret = []

    for key in adb.list_packages(None):
        app = store.get_app_by_pkgname(key)
        if not app:
            continue
        # Only want desktop apps here
        if app.get_kind() != As.AppKind.DESKTOP:
            continue
        ret.append(key)
    return ret


def filter_packages_by_data(adb, store):
    """ Return available packages by appdata only """
    pkgs = find_have_data(adb, store)
    ret = []
    for item in pkgs:
        pkg = adb.get_package(item)
        ret.append(pkg)
    return ret


def unmangle_date(tstamp):
    try:
        ret = time.strptime(tstamp, "%Y-%m-%d")
        return ret
    except Exception:
        # Probably because old eopkg pspec
        pass
    try:
        ret = time.strptime(tstamp, "%m-%d-%Y")
        return ret
    except Exception:
        return 0


def history_sort(pkgA, pkgB):
    dateA = pkgA.history[0].date
    dateB = pkgB.history[0].date
    aa = unmangle_date(dateA)
    ab = unmangle_date(dateB)

    return cmp(aa, ab)


# Mandatory components, removing will cause imminent death
essential_components = [
    "system.base",
]


# Essential packages, removing will upset and lead to imminent death.
essential_packages = [
    "mesalib",
    "xorg-server",
    "dhcpcd",
    "network-manager",
    "wpa_supplicant",
]


# Utter laziness. :P
ICON_MAPS = {
    "desktop": "user-desktop",
    "desktop.budgie": "start-here-solus",
    "desktop.core": "system-run",
    "desktop.font": "fonts",
    "desktop.gnome": "desktop-environment-gnome",
    "desktop.gnome.core": "system-devices-information",
    "desktop.gnome.doc": "folder-documents",
    "desktop.gtk": "gtk-dialog-info",
    "desktop.kde": "desktop-environment-kde",
    "desktop.library": "emblem-shared-symbolic",
    "desktop.mate": "mate",
    "desktop.multimedia": "multimedia-volume-control",
    "desktop.qt": "qtconfig-qt4",
    "desktop.theme": "preferences-desktop-wallpaper",
    "editor": "x-office-document",
    "games": "applications-games",
    "games.action": "dota2",
    "games.arcade": "gnome-nibbles",
    "games.card": "gnome-aisleriot",
    "games.emulator": "ds-emulator",
    "games.puzzle": "gnome-tetravex",
    "games.rpg": "wesnoth",
    "games.strategy": "games-endturn",
    "multimedia.sound": "multimedia-volume-control",
    "multimedia.video": "camera-video",
    "multimedia.audio": "library-music",
    "multimedia.graphics": "camera-photo",
    "network.download": "transmission",
    "network.email": "internet-mail",
    "network.im": "empathy",
    "network.irc": "hexchat",
    "network.news": "internet-news-reader",
    "network.web": "emblem-web",
    "network.web.browser": "web-browser",
    "office": "x-office-spreadsheet",
    "office.finance": "homebank",
    "office.maths": "gnome-calculator",
    "office.scientific": "applications-science",
    "office.notes": "gnote",
    "office.viewers": "calibre-viewer",
    "programming.devel": "text-x-changelog",
    "programming.haskell": "applications-haskell",
    "programming.ide": "text-editor",
    "programming.java": "applications-java",
    "programming.python": "application-x-python-bytecode",
    "programming.tools": "gitg",
    "security": "preferences-system-firewall",
}


def is_essential_package(pkg):
    """ Essential packages should NEVER be removed by the user. """
    if pkg.partOf in essential_components:
        return True
    if pkg.name in essential_packages:
        return True
    return False


class EopkgSource(ProviderSource):
    """ EopkgSource wraps a repository object """

    active = None
    url = None
    name = None
    plugin = None
    __gtype_name__ = "NxEopkgSource"

    def get_name(self):
        return self.name

    def __init__(self, rdb, repoName):
        ProviderSource.__init__(self)
        self.url = rdb.get_repo_url(repoName)
        self.name = repoName
        self.active = rdb.repo_active(repoName)

    def describe(self):
        ret = "{} - {}".format(self.name, self.url)
        if not self.active:
            ret += " (inactive)"
        return ret


class EopkgGroup(ProviderCategory):
    """ Wraps a GroupDB entry for top level groups """

    id = None
    group = None
    children = None

    def __init__(self, groupID, group):
        ProviderCategory.__init__(self)
        self.id = groupID
        self.group = group
        self.children = []

        # Just replace the icon on the fly with something that
        # fits better into the current theme
        settings = Gtk.Settings.get_default()
        icon_theme = settings.get_property("gtk-icon-theme-name")
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

        icon = str(self.group.icon)
        if icon in replacements:
            self.icon = replacements[icon]
        else:
            self.icon = icon

    def get_children(self):
        return self.children

    def get_name(self):
        return str(self.group.localName)

    def get_id(self):
        return str(self.id)

    def get_icon_name(self):
        """ Return internal eopkg group icon name """
        return self.icon


class EopkgComponent(ProviderCategory):
    """ Wraps an eopkg component """

    id = None
    comp = None

    def __init__(self, compID, comp):
        ProviderCategory.__init__(self)
        self.id = compID
        self.comp = comp

    def get_name(self):
        return str(self.comp.localName)

    def get_id(self):
        return str(self.id)

    def get_icon_name(self):
        if str(self.id) in ICON_MAPS:
            return ICON_MAPS[str(self.id)]
        return "package-x-generic"


class EopkgPlugin(ProviderPlugin):
    """ EopkgPlugin interfaces with the eopkg package manager """

    availDB = None
    installDB = None
    groupDB = None
    compDB = None
    cats = None

    repos = None

    # pisi crap
    link = None
    pmanager = None

    # Allow us to track expected operations for progress purposes
    progress_total = 0    # Total number of items in our operation
    progress_current = 0  # Current progress
    current_package = None

    operation_blocked = False  # Allow spin locking

    __gtype_name__ = "NxEopkgPlugin"

    def __init__(self):
        ProviderPlugin.__init__(self)
        self.availDB = pisi.db.packagedb.PackageDB()
        self.installDB = pisi.db.installdb.InstallDB()
        self.repoDB = pisi.db.repodb.RepoDB()
        self.groupDB = pisi.db.groupdb.GroupDB()
        self.compDB = pisi.db.componentdb.ComponentDB()

        # Talk to eopkg/pisi over dbus
        self.link = comar.Link()
        try:
            self.link.setLocale()
        except Exception as e:
            print("Failure to set locale: {}".format(e))

        self.pmanager = self.link.System.Manager['pisi']
        self.link.listenSignals("System.Manager", self.dbus_callback)

        self.build_categories()

    def build_categories(self):
        """ Find all of our possible categories and nest them. """
        self.cats = []
        groups = self.groupDB.list_groups()
        groups.sort()
        for groupID in groups:
            group = self.groupDB.get_group(groupID)
            item = EopkgGroup(groupID, group)

            components = self.groupDB.get_group_components(groupID)
            components.sort()

            for compID in components:
                comp = self.compDB.get_component(compID)
                childItem = EopkgComponent(compID, comp)
                item.children.append(childItem)

            self.cats.append(item)

    def categories(self):
        return self.cats

    def sources(self):
        repos = []
        mainRepos = self.repoDB.list_repos(only_active=False)
        for x in mainRepos:
            repo = EopkgSource(self.repoDB, x)
            repo.parent_plugin = self
            repos.append(repo)
        return repos

    def populate_storage(self, storage, popfilter, extra):
        if popfilter == PopulationFilter.INSTALLED:
            return self.populate_installed(storage)
        elif popfilter == PopulationFilter.SEARCH:
            return self.populate_search(storage, extra)
        elif popfilter == PopulationFilter.RECENT:
            return self.populate_recent(storage, extra)
        elif popfilter == PopulationFilter.NEW:
            return self.populate_new(storage, extra)
        elif popfilter == PopulationFilter.FEATURED:
            return self.populate_featured(storage, extra)
        elif popfilter == PopulationFilter.CATEGORY:
            return self.populate_category(storage, extra)
        elif popfilter == PopulationFilter.UPDATES:
            self.populate_updates(storage, extra)

    def populate_recent(self, storage, appsystem):
        """ Populate home view with recently updated packages """

        limit = 20  # Arbitrary right now

        inp = filter_packages_by_data(self.availDB, appsystem.store)
        inp.sort(history_sort, reverse=True)
        if len(inp) > limit:
            inp = inp[0:limit]

        for pkg in inp:
            item = self.build_item(pkg.name)
            storage.add_item(item.get_id(), item, PopulationFilter.RECENT)

    def populate_new(self, storage, appsystem):
        """ Populate home view with recently uploaded packages """

        # Hack for demo
        news = [
            "gnome-weather",
            "gnome-mpv",
            "kdenlive",
            "hexchat",
            "dustrac",
        ]

        for i in news:
            item = self.build_item(i)
            storage.add_item(item.get_id(), item, PopulationFilter.NEW)

    def populate_featured(self, storage, appsystem):
        """ Populate home view with "hot" packages """

        # Hack for demo
        news = [
            "sayonara-player",
            "pitivi",
            "libreoffice-writer",
            "kdeconnect",
            "polari",
            "tilix",
            "inkscape",
            "gnome-boxes",
        ]

        for i in news:
            item = self.build_item(i)
            storage.add_item(item.get_id(), item, PopulationFilter.NEW)

    def populate_search(self, storage, request):
        """ Attempt to search for a given term in the DB """
        # Trick eopkg into searching through spaces and hyphens
        term = request.get_term().replace(" ", "[-_ ]").replace(".", "\.")
        term = term.replace("+", "\+").replace("?", "\?")

        srslt = set()
        try:
            if not request.get_installed_only():
                srslt.update(self.availDB.search_package([term]))
            srslt.update(self.installDB.search_package([term]))
        except Exception as e:
            # Invalid regex, basically, from someone smashing FIREFOX????
            print(e)
            return

        leaders = difflib.get_close_matches(term.lower(),
                                            srslt, cutoff=0.5)
        packages = leaders
        packages.extend(sorted([x for x in srslt if x not in leaders]))

        count = 0

        for item in packages:
            if count >= 100:
                break

            # Skip devel stuff in search results
            if item.endswith("-dbginfo") or item.endswith("-devel"):
                if "dbginfo" not in term and "devel" not in term:
                    continue

            pkg = self.build_item(item)

            count += 1

            storage.add_item(pkg.get_id(), pkg, PopulationFilter.SEARCH)
        print("eopkg done!")

    def populate_installed(self, storage):
        """ Populate from the installed filter """
        for pkgID in self.installDB.list_installed():
            pkg = self.build_item(pkgID)
            storage.add_item(pkg.get_id(), pkg, PopulationFilter.INSTALLED)

    def populate_category(self, storage, category):
        """ Ask componentDB for all packages in the given component """
        pkgs = self.compDB.get_packages(category.get_id(), None, False)
        for pkgID in pkgs:
            pkg = self.build_item(pkgID)
            storage.add_item(pkg.get_id(), pkg, PopulationFilter.CATEGORY)

    def populate_updates(self, storage, extra):
        """ Find all available updates for the currently installed software
            Note: This is incredibly primitive and has no plan facility """
        # This does account for stuff that is set to be replaced
        pkgs = pisi.api.list_upgradable()
        for pkgID in pkgs:
            pkg = self.build_item(pkgID)
            storage.add_item(pkg.get_id(), pkg, PopulationFilter.UPDATES)

    def build_item(self, name):
        """ Build a complete item definition """
        avail = None
        installed = None
        if self.availDB.has_package(name):
            avail = self.availDB.get_package(name)
        if self.installDB.has_package(name):
            installed = self.installDB.get_package(name)
        item = EopkgItem(installed, avail)
        item.parent_plugin = self
        return item

    def plan_install_item(self, item):
        """ Plan the installation of a given item """
        trans = Transaction(item)

        # Push the installation set here
        (pg, pkgs) = plan_install_pkg_names([item.get_id()])
        for name in pkgs:
            if self.installDB.has_package(name):
                # Have the package so its an update now
                trans.push_upgrade(self.build_item(name))
            else:
                # Newly installed through dependency
                trans.push_installation(self.build_item(name))

        # Potential conflict?
        conflicts = pisi_helper.check_conflicts(pkgs, self.availDB)
        if conflicts:
            for name in conflicts:
                trans.push_removal(self.build_item(name))

        return trans

    def plan_remove_item(self, item, automatic=False):
        """ Plan removal of a given item """
        trans = Transaction(item)

        if not automatic:
            (pg, pkgs) = plan_remove([item.get_id()])
        else:
            (pg, pkgs) = plan_autoremove([item.get_id()])

        for name in pkgs:
            trans.push_removal(self.build_item(name))

        return trans

    def spinlock_busy_wait(self):
        """ Prep us for a new spinlock cycle """
        print(" -> Prep spinlock")
        self.operation_blocked = True

    def spinlock_busy_end(self):
        """ Wait until we're unblocked basically, with minimal wakes """
        print(" -> spinlock start")
        while self.operation_blocked:
            time.sleep(.500)
        print(" -> spinlock end")

    def dbus_callback(self, package, signal, args):
        """ eopkg/pisi talked to us via COMAR """

        # Proxy the request to the appropriate callback
        if signal == "status":
            self.handle_dbus_status(args)
        elif signal == "progress":
            self.handle_dbus_progress(args)
        elif signal == "finished" or signal is None:
            self.handle_dbus_finished(args)
        elif str(signal).startswith("tr.org.pardus.comar.Comar.PolicyKit"):
            self.handle_dbus_cancelled(args)

    def handle_dbus_status(self, args):
        """ Handle status command appropriately """
        cmd = args[0]
        what = args[1]

        # Unlike old SC we no longer look for configuring step as usysconf
        # does this once we're all complete.

        if cmd == "upgrading":
            self.handle_dbus_upgrading(what)
        elif cmd == "upgraded":
            self.handle_dbus_upgraded(what)
        elif cmd == "removing":
            self.handle_dbus_removing(what)
        elif cmd == "removed":
            self.handle_dbus_removed(what)
        elif cmd == "installing":
            self.handle_dbus_installing(what)
        elif cmd == "installed":
            self.handle_dbus_installed(what)
        elif cmd == "extracting":
            self.handle_dbus_extracting(what)
        elif cmd == "systemconf":
            self.handle_dbus_usysconf()
        elif cmd == "updatingrepo":
            self.handle_dbus_repo_update()
        else:
            print("Status: {} {}".format(cmd, what))

    def handle_dbus_upgrading(self, what):
        """ Package is now upgrading """
        self.current_package = what
        self.executor.set_progress_string(_("Upgrading {} of {}: {}".format(
            self.progress_current + 1,
            self.progress_total,
            self.current_package)))

    def handle_dbus_upgraded(self, what):
        """ Package was upgraded """
        self.executor.set_progress_string(_("Upgraded {} of {}: {}".format(
            self.progress_current + 1,
            self.progress_total,
            self.current_package)))
        self.progress_current += 1

    def handle_dbus_removing(self, what):
        """ Package is now removing """
        self.current_package = what
        self.executor.set_progress_string(_("Removing {} of {}: {}".format(
            self.progress_current + 1,
            self.progress_total,
            self.current_package)))

    def handle_dbus_removed(self, what):
        """ Package was removed """
        self.executor.set_progress_string(_("Removed {} of {}: {}".format(
            self.progress_current + 1,
            self.progress_total,
            self.current_package)))
        self.progress_current += 1

    def handle_dbus_installing(self, what):
        """ Package is now installing """
        self.current_package = what
        self.executor.set_progress_string(_("Installing {} of {}: {}".format(
            self.progress_current + 1,
            self.progress_total,
            self.current_package)))

    def handle_dbus_installed(self, what):
        """ Package was installed """
        self.executor.set_progress_string(_("Installed {} of {}: {}".format(
            self.progress_current + 1,
            self.progress_total,
            self.current_package)))
        self.progress_current += 1

    def handle_dbus_extracting(self, what):
        self.current_package = what
        self.executor.set_progress_string(_("Extracting {} of {}: {}".format(
            self.progress_current + 1,
            self.progress_total,
            self.current_package)))

    def handle_dbus_usysconf(self):
        self.executor.set_progress_string(_("Updating system configuration"))

    def handle_dbus_repo_update(self):
        self.executor.set_progress_string(_("Updating repository information"))

    def handle_dbus_progress(self, args):
        """ Handle progress changes """
        print("Progress: {}".format(args))

    def handle_dbus_finished(self, args):
        """ Handle D-BUS finish, i.e. rebuild caches and such """
        finishedTypes = [
            "System.Manager.installPackage",
            "System.Manager.reinstallPackage",
            "System.Manager.removePackage",
            "System.Manager.updatePackage",
            "System.Manager.updateRepository",
            "System.Manager.updateAllRepositories",
        ]
        if args and args[0] and args[0] in finishedTypes:
            # This is where we need to force a rebuild of the context
            print("Finished: {}".format(args[0]))
            # Unblock spin lock here
            self.operation_blocked = False

        print("Finished message: {}".format(args))

    def handle_dbus_cancelled(self, args):
        """ Cancellation or failure to authenticate """
        print("Cancellation: {}".format(args))

    def install_item(self, executor, items):
        names = [x.get_id() for x in items]
        print("installing: {}".format(names))
        # Stash executor for dbus callback
        self.executor = executor

        # Guard operation to ensure we complete all ops
        self.spinlock_busy_wait()
        self.pmanager.installPackage(",".join(names))
        self.spinlock_busy_end()

        # Drop it again
        self.executor = None

    def refresh_source(self, executor, source):
        print("Refreshing source: {}".format(source.get_name()))
        self.executor = executor

        self.spinlock_busy_wait()
        self.pmanager.updateRepository(source.get_name())
        self.spinlock_busy_end()

        self.executor = None


class EopkgItem(ProviderItem):
    """ EopkgItem abstracts access to the native package type, i.e. eopkg """

    installed = None
    available = None
    displayCandidate = None

    __gtype_name__ = "NxEopkgItem"

    def __init__(self, installed, available):
        ProviderItem.__init__(self)
        self.installed = installed
        self.available = available

        self.add_status(ItemStatus.META_CHANGELOG)

        if self.installed is not None:
            self.displayCandidate = self.installed
            self.add_status(ItemStatus.INSTALLED)
            relOld = self.installed.history[0].release
            relNew = relOld
            if self.available:
                relNew = self.available.history[0].release
            if relNew > relOld:
                self.add_status(ItemStatus.UPDATE_NEEDED)
        else:
            self.displayCandidate = self.available

        # Is this an essential item?
        if self.available and is_essential_package(self.available):
            self.add_status(ItemStatus.META_ESSENTIAL)

        name = self.get_name()
        if name.endswith("-dbginfo") or name.endswith("-devel"):
            self.add_status(ItemStatus.META_DEVEL)

    def get_id(self):
        return str(self.displayCandidate.name)

    def get_name(self):
        return self.displayCandidate.name

    def get_summary(self):
        return str(self.displayCandidate.summary)

    def get_title(self):
        return str(self.displayCandidate.name)

    def get_description(self):
        return str(self.displayCandidate.description)

    def get_version(self):
        return self.displayCandidate.history[0].version
